# Очки за прогноз по типу события (синхронизируйте с EVENT_TYPE_POINTS во frontend/index.html)
POINTS_BY_EVENT_TYPE: dict[str, int] = {
    "goal": 100,
    "save": 100,
    "foul": 100,
    "moment": 100,
    "frag": 110,
    "ace": 150,
    "objective": 120,
    "round": 100,
}


def prediction_points_for_event(event_type: str) -> int:
    if not event_type:
        return 100
    return POINTS_BY_EVENT_TYPE.get(event_type, 100)
