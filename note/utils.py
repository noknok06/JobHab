from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from django.conf import settings

# フォントのパス
FONT_PATH = os.path.join(settings.STATIC_ROOT, "fonts/NotoSansCJKjp-Regular.ttf")

# フォント登録
pdfmetrics.registerFont(TTFont('NotoSansJP', FONT_PATH))
