# Website and gallery maintenance

The site has a landing page and two subpages: **Tutorial** and **Gallery**. The tutorial is generated directly from `README.md`, so its content stays synchronized with the repository. The gallery is generated from `website/gallery.json`.

## Preview locally

From the repository root:

```bash
python -m pip install -r requirements-site.txt
python scripts/build_site.py
python scripts/check_site.py
python -m http.server 8000 --directory _site
```

Open <http://localhost:8000>. Stop the server with Ctrl+C. The site uses local CSS, JavaScript, and images; it does not depend on a CDN, analytics service, or live GitHub API calls.

Generated files are written to `_site/`, which is ignored by Git. Rebuild after editing the README, gallery entries, templates, or assets. Relative links support the repository's GitHub Pages subdirectory.

## Publish on GitHub Pages

The workflow in `.github/workflows/pages.yml` builds and checks the site on pull requests and pushes to `main`. Publishing requires these repository settings and a push; local editing alone does not publish it.

1. Commit and push the reviewed source files when ready.
2. In the GitHub repository, open **Settings → Pages**.
3. Under **Build and deployment → Source**, select **GitHub Actions**.
4. Run **Build and deploy GitHub Pages** from the Actions tab, or push another change to `main`.

After a successful deployment, the expected addresses are:

- Home: <https://VibeCodingMICCAI.github.io/stand4_scientific_figure/>
- Tutorial: <https://VibeCodingMICCAI.github.io/stand4_scientific_figure/tutorial/>
- Gallery: <https://VibeCodingMICCAI.github.io/stand4_scientific_figure/gallery/>

See [GitHub's custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) for publishing requirements.

## Submit a figure

The gallery's submission buttons open `.github/ISSUE_TEMPLATE/figure-submission.yml` in this repository. Submissions collect the paper and figure number, reference and reproduced images, code, run instructions, data provenance, design lessons, and attribution.

Issues do **not** appear in the gallery automatically. Maintainers review the material, then add accepted examples to `website/gallery.json`. This also keeps the website usable without GitHub API access.

## Add an accepted entry

1. Put the reference and reproduced/adapted images in `assets/`.
2. Put plotting code in `scripts/` and shareable data in `sample-datasets/`. For diagrams, provide the editable source and link it from the entry or contribution issue.
3. Add an object to `website/gallery.json`, following an existing entry. Use a unique lowercase `id` with hyphens. Record whether the work is a design adaptation, numerical reproduction, or approximate reconstruction.
4. Add an `Original author contribution` credit only after confirming authorship. Keep the original creators' attribution and any available reuse terms with the entry. Link the accepted submission in the credit if helpful.
5. Run the build and link checks, inspect the site, and submit the change for review.

The fields `image`, `reference_image`, and `code` refer to local files. `data` may be `null` when values are embedded in the script. `extra_data` is optional. The builder copies local assets, scripts, and datasets into the static site so visitors can download them.

Current examples preserve the supplied tutorial images. Some values are approximate, and the results examples include interpretation notes. Downloaded code should be checked and run with its documented dependencies.
