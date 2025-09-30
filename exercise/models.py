#FitSpin/exercise/models.py
from django.db import models

# この運動がどのレベルのガチャに登場するかchoicesを使う
LEVEL_CHOICES = [
        (1, 'レベル1'),
        (2, 'レベル2'),
        (3, 'レベル3'),
        (4, 'レベル4'),
        (5, 'レベル5'),
]

# ガチャで表示する運動の各項目（運動名、回数/時間、対象レベル）をフィールドとして持つ Exercise モデルを作成
class Exercise(models.Model):
  # 運動の名称 (例: スクワット、深呼吸)
 name =models.CharField(max_length=255, unique=False, verbose_name="運動名")
 level = models.IntegerField(choices=LEVEL_CHOICES, verbose_name="対象レベル")
 description = models.TextField(blank=True, null=True, verbose_name="説明")
 # 追加：スペシャル運動かどうか
 is_special = models.BooleanField(default=False, verbose_name="スペシャル運動かどうか")


class Meta:
  verbose_name = "運動"
  verbose_name_plural = "運動"

def __str__(self):
    return f"Lv.{self.level}: {self.name} ({'スペシャル' if self.is_special else '通常'})"
