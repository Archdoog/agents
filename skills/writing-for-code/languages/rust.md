# Rust Documentation

Fetch the official rustdoc guide once per session before documenting a public API.
Baseline: [Rust 1.91.0: writing documentation](https://doc.rust-lang.org/1.91.0/rustdoc/how-to-write-documentation.html).
For examples, also use [Rust 1.91.0: what to include](https://doc.rust-lang.org/1.91.0/rustdoc/write-documentation/what-to-include.html).
Check the repository's toolchain and minimum supported Rust version.

Use `///` for an item and `//!` for the containing module or crate.
Start with a useful summary. Describe parameter meaning without repeating types already present in the signature.
Include `# Errors`, `# Panics`, `# Safety`, and `# Examples` when applicable.
For unsafe APIs, state the caller's safety obligations precisely.
Distinguish returned errors from panics and violations that can cause undefined behavior.

Explain units, lifetimes, ownership, resource release, and concurrency limits that types alone do not convey.
Keep implementation constraints when a maintainer needs them to preserve safety.
Give crate and module overviews with a real use case and links to public entry points.

Make examples valid for the supported toolchain. Hidden setup must not hide an essential caller requirement.
Run the repository's documentation tests when available. Do not label an example tested without a run.
