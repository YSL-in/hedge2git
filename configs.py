from dotenv import dotenv_values

configs: dict[str, str] = dotenv_values()  # type: ignore
configs['HEDGEDOC_SERVER'] += '/' if not configs['HEDGEDOC_SERVER'].endswith('/') else configs['HEDGEDOC_SERVER']
