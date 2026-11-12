# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx>=0.28,<1"]
# ///
"""Read PR feedback, post replies, and resolve threads through the CLI."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx

_METADATA = """
query($owner:String!,$repo:String!,$pr:Int!){
  viewer{login}
  repository(owner:$owner,name:$repo){pullRequest(number:$pr){
    url author{login} baseRefName headRefName headRefOid
    baseRepository{nameWithOwner} headRepository{nameWithOwner}
  }}
}
"""
_THREAD_COMMENTS = """
query($id:ID!,$cursor:String){
  node(id:$id){... on PullRequestReviewThread{
    comments(first:100,after:$cursor){
      nodes{databaseId author{login} body url} pageInfo{hasNextPage endCursor}
    }
  }}
}
"""
_RESOLVE = """
mutation($threadId:ID!){
  resolveReviewThread(input:{threadId:$threadId}){thread{isResolved}}
}
"""


def _gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout.strip()


def _graphql(client, query, variables):
    path = "/graphql" if client.base_url.host == "api.github.com" else "/api/graphql"
    url = client.base_url.copy_with(path=path)
    response = client.post(url, json={"query": query, "variables": variables})
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise ValueError(
            "GitHub rejected the GraphQL request. Check account permissions and API limits."
        )
    if not payload.get("data"):
        raise ValueError("GitHub returned no GraphQL data.")
    return payload["data"]


def _pages(client, query, variables, path):
    nodes = []
    cursor = None
    seen = set()
    while True:
        connection = _graphql(client, query, dict(variables, cursor=cursor))
        for key in path:
            connection = connection[key]
        nodes.extend(connection["nodes"])
        page = connection["pageInfo"]
        if not page["hasNextPage"]:
            return nodes
        cursor = page["endCursor"]
        if not cursor or cursor in seen:
            raise ValueError("GitHub returned an invalid pagination cursor.")
        seen.add(cursor)


def _pr_connection(client, variables, field, selection):
    query = """
    query($owner:String!,$repo:String!,$pr:Int!,$cursor:String){
      repository(owner:$owner,name:$repo){pullRequest(number:$pr){
        %s(first:100,after:$cursor){
          nodes{%s} pageInfo{hasNextPage endCursor}
        }
      }}
    }
    """ % (field, selection)
    return _pages(client, query, variables, ("repository", "pullRequest", field))


def _login(author):
    return author["login"] if author else None


def _comment(comment):
    return {"author": _login(comment["author"]), "body": comment["body"], "url": comment["url"]}


def _feedback(client, repository, pr):
    owner, repo = repository.split("/")
    variables = {"owner": owner, "repo": repo, "pr": pr}
    metadata = _graphql(client, _METADATA, variables)
    pull = metadata["repository"]["pullRequest"]
    if pull is None:
        raise ValueError("The pull request does not exist or is not accessible.")
    threads = _pr_connection(
        client, variables, "reviewThreads", "id isResolved isOutdated path line"
    )
    unresolved = []
    for thread in threads:
        if thread["isResolved"]:
            continue
        comments = _pages(client, _THREAD_COMMENTS, {"id": thread["id"]}, ("node", "comments"))
        unresolved.append(
            {
                "thread_id": thread["id"],
                "reply_to": comments[0]["databaseId"] if comments else None,
                "path": thread["path"],
                "line": thread["line"],
                "outdated": thread["isOutdated"],
                "comments": [_comment(comment) for comment in comments],
            }
        )
    comments = _pr_connection(client, variables, "comments", "author{login} body url")
    reviews = _pr_connection(
        client, variables, "reviews", "author{login} body url state commit{oid}"
    )
    return {
        "pr": pr,
        "url": pull["url"],
        "author": _login(pull["author"]),
        "viewer": metadata["viewer"]["login"],
        "base_ref": pull["baseRefName"],
        "head_ref": pull["headRefName"],
        "head_oid": pull["headRefOid"],
        "base_repository": pull["baseRepository"]["nameWithOwner"],
        "head_repository": (pull["headRepository"] or {}).get("nameWithOwner"),
        "unresolved_threads": unresolved,
        "top_level_comments": [_comment(comment) for comment in comments],
        "reviews": [
            dict(
                _comment(review), state=review["state"], commit=(review["commit"] or {}).get("oid")
            )
            for review in reviews
        ],
    }


def _positive_number(value):
    if not re.fullmatch(r"[1-9][0-9]*", value):
        raise argparse.ArgumentTypeError("Expected a positive integer.")
    return int(value)


def _thread_id(value):
    if not re.fullmatch(r"PRRT_[A-Za-z0-9_-]+", value):
        raise argparse.ArgumentTypeError("Expected a PRRT_ thread ID.")
    return value


def _parser():
    parser = argparse.ArgumentParser(description="Read and address GitHub PR feedback.")
    commands = parser.add_subparsers(dest="command", required=True)
    read = commands.add_parser("list", help="Read all PR feedback as JSON.")
    read.add_argument(
        "pr", type=_positive_number, nargs="?", help="Default: the current branch's PR."
    )
    reply = commands.add_parser("reply", help="Post an inline or conversation reply.")
    reply.add_argument("pr", type=_positive_number)
    target = reply.add_mutually_exclusive_group(required=True)
    target.add_argument("--comment", type=_positive_number, help="Inline comment database ID.")
    target.add_argument("--top", action="store_true", help="Post a PR conversation comment.")
    body = reply.add_mutually_exclusive_group(required=True)
    body.add_argument("--body", help="Reply text.")
    body.add_argument("--body-file", type=Path, help="UTF-8 file with reply text.")
    resolve = commands.add_parser("resolve", help="Resolve an addressed inline thread.")
    resolve.add_argument("thread", type=_thread_id)
    return parser


def _execute(args, client, repository):
    if args.command == "list":
        pr = args.pr
        if pr is None:
            pr = json.loads(_gh("pr", "view", "--json", "number"))["number"]
        return json.dumps(_feedback(client, repository, pr), indent=2)
    if args.command == "reply":
        if args.top:
            endpoint = f"repos/{repository}/issues/{args.pr}/comments"
        else:
            endpoint = f"repos/{repository}/pulls/{args.pr}/comments/{args.comment}/replies"
        response = client.post(endpoint, json={"body": args.body})
        response.raise_for_status()
        return response.json()["html_url"]
    data = _graphql(client, _RESOLVE, {"threadId": args.thread})
    if data["resolveReviewThread"]["thread"]["isResolved"] is not True:
        raise ValueError("GitHub did not resolve the thread.")
    return "true"


def _main(argv=None):
    args = _parser().parse_args(argv)
    try:
        if args.command == "reply":
            if args.body_file is not None:
                args.body = args.body_file.read_text(encoding="utf-8")
            if not args.body.strip():
                raise ValueError("The reply body must not be empty.")
        metadata = json.loads(_gh("repo", "view", "--json", "nameWithOwner,url"))
        host = urlsplit(metadata["url"]).hostname
        token = _gh("auth", "token", "--hostname", host)
        base_url = "https://api.github.com/" if host == "github.com" else f"https://{host}/api/v3/"
        with httpx.Client(
            base_url=base_url,
            timeout=30,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        ) as client:
            result = _execute(args, client, metadata["nameWithOwner"])
        print(result)
        return 0
    except subprocess.CalledProcessError:
        print("GitHub CLI failed. Check the checkout and authentication.", file=sys.stderr)
    except httpx.HTTPStatusError as error:
        print(
            f"GitHub returned HTTP {error.response.status_code}. Check permissions and API limits.",
            file=sys.stderr,
        )
    except httpx.RequestError:
        print("The GitHub request failed. Check the network connection.", file=sys.stderr)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Cannot complete the request: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(_main())
