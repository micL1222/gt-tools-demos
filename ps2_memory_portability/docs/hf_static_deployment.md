# Hugging Face Static Space Deployment

This package is designed for a free, zero-build Static Space. It does not use
Gradio, Python, Docker, a backend, or a paid hosting plan.

## Public Deployment

The manual deployment is complete.

- URL: https://huggingface.co/spaces/mickeystk/ps2-stay-or-switch-memory-portability
- Owner: `mickeystk`
- Slug: `ps2-stay-or-switch-memory-portability`
- Visibility: Public
- SDK: Static
- Deployment revision: `9ffb3cadcb80d558cb1d4473d227a383b8a5aa50`
- Verification: the public Space API reported `private: false`, `sdk: static`, and
  runtime stage `RUNNING`; the static host served `index.html`, `styles.css`,
  `app.js`, and `scenarios.json` successfully.

The browser verification covered the complete `FULL_030` interaction and
benchmark checks for `PARTIAL_045` and `NONE_045`. The peer-comparison scope is
limited to the current browser-page session. There is no backend or persistent
behavioral store, so this deployment does not create a cross-visitor dataset.

## Original manual-upload procedure

1. Log in to Hugging Face account `mickeystk`.
2. Go to **Spaces** and click **Create new Space**.
3. Name the Space `ps2-stay-or-switch-memory-portability`.
4. Set visibility to **Public**.
5. Select SDK **Static**.
6. Create the Space.
7. Open its **Files** tab.
8. Upload exactly the five files listed below from
   `ps2_memory_portability/behavioral_static_space/`:

   ```text
   README.md
   index.html
   styles.css
   app.js
   scenarios.json
   ```

9. Commit/upload the files through the Hugging Face web interface and wait for
   the static page to render.
10. Verify that the main page opens and that `?scenario=FULL_030` displays the
    expected Switch benchmark after reveal.
11. Run the complete [manual test checklist](static_behavioral_manual_test.md).
12. If the Space is recreated, record its actual public URL and revision in
    this section after repeating the verification checks above.

`README.md` must be uploaded because its YAML front matter declares
`sdk: static` and `app_file: index.html`. Do not select Gradio and do not upload
the original `behavioral_space/` prototype, tests, outputs, credentials, or
this repository as a whole.

Static peer comparison is intentionally local to the current browser-page
session; it does not create a shared behavioral dataset.
