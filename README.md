# codex

This repository now includes a helper script for downloading the `pygame` wheel using `pip`.

## Downloading pygame

Run the following command from the repository root:

```bash
scripts/download_pygame.sh
```

By default it saves the downloaded artifacts into the `vendor/` directory. You can pass a
custom directory as the first argument if desired.

> **Note:** The execution environment used to generate this change does not have outbound
> network access, so the download command will fail here. Run the script on a machine with
> Internet connectivity to obtain the packages.
