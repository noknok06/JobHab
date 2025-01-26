def __init__(self, *args, **kwargs):
    note = kwargs.get('instance')
    if note and note.pk:
        initial_tags = ', '.join(note.tags.values_list('name', flat=True))  # より簡潔な取得方法
        kwargs.setdefault('initial', {}).setdefault('tags', initial_tags)  # 既存の initial を上書きしない
    super().__init__(*args, **kwargs)
