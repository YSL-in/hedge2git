from dotenv import dotenv_values

configs: dict[str, str] = dotenv_values()  # type: ignore
