def select(
    cur, fields: list[str], table: str, where: str = "", params: dict = {}
) -> list:
    field_list = ",".join(fields)
    statement = f"SELECT {field_list} FROM {table}"
    if where != "":
        statement = f"{statement} WHERE {where}"
    cur.execute(statement, params)
    rows = cur.fetchall()
    return rows
