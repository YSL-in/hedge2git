hedge2git
===

As the name implies, this is a sync tool to upload/download notes from/to Hedgedoc to/from Git repositories and more.

Hedgedoc does not support hierarchical structure of notes, such as the concept of folders or the book mode from HackMD,
while this tool builds the hierarchy based on the tags which can be specified in 3 ways:

- via csv format in YAML metadata from the very beginning of the note.

```markdown
---
tags: TAG1, TAG2, TAG3
---

TITLE
===
```

- via list format in YAML metadata from the very beginning of the note.

```markdown
---
title: TITLE
tags:
  - TAG1
  - TAG2
  - TAG3
---

...
```

- via tag header in the note content

```markdown
###### tags: `TAG1` `TAG2` `TAG3`
```

Usage
---

- Make a copy of *.env.example* and name it as *.env*.
- Fill in all the blanks and modify the pre-filled based on your case.
  - `DB_TYPE` specifies the database management system type. Postgres is currently the only one tested.
  - `DB_USER` and `DB_PASS` are the credentials to access the database `DB_NAME` on the host `DB_HOST`
    at the port `DB_PORT`. There are limited APIs provided by the Hedgedoc, and thus some actions need to be done
    via DB operations.
  - `HEDGEDOC_USER` and `HEDGEDOC_PASS` are the credentials to access the Hedgedoc server at `HEDGEDOC_SERVER`.
  - `GIT_REPO` is the git repository to store the Hedgedoc notes.
  - `GIT_REF` is the git branch to store the Hedgedoc notes.
  - `GIT_USER` and `GIT_EMAIL` are used in commits to store the Hedgedoc notes.

```bash
pipenv install
pipenv run python hedge2git --help

# upload
pipenv run python hedge2git --push
pipenv run python hedge2git --push "First sync from $HOSTNAME"
pipenv run python hedge2git --push --push-type=overwrite --dry-run

# download
pipenv run python hedge2git --pull
pipenv run python hedge2git --pull --pull-type=overwrite --dry-run
```
