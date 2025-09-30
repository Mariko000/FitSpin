# import_special_exercises.py
import csv
from django.core.management.base import BaseCommand, CommandError
from exercise.models import Exercise, LEVEL_CHOICES  # LEVEL_CHOICES をインポート

class Command(BaseCommand):
    help = 'special_exercises.csv から Exercise モデルにデータを取り込む'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='special_exercises.csv',
            help='CSVファイルのパス'
        )

    def handle(self, *args, **options):
        csv_path = options['file']
        self.stdout.write(self.style.NOTICE(f'CSV読み込み: {csv_path}'))

        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                imported_count = 0
                updated_count = 0
                skipped_count = 0

                for row in reader:
                    name = row.get('name')
                    level_str = row.get('level')
                    description = row.get('description', '')

                    if not name or not level_str:
                        self.stdout.write(self.style.WARNING(f"スキップ: 名前またはレベル不足 - {row}"))
                        skipped_count += 1
                        continue

                    try:
                        level = int(level_str)
                        if level not in [choice[0] for choice in LEVEL_CHOICES]:
                            self.stdout.write(self.style.WARNING(f"スキップ: 不正なレベル値 '{level_str}' - {row}"))
                            skipped_count += 1
                            continue
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"スキップ: レベルが数値ではない - {row}"))
                        skipped_count += 1
                        continue

                    is_special = row.get('is_special', 'True') == 'True'

                    try:
                        obj, created = Exercise.objects.update_or_create(
                            name=name,
                            level=level,
                            defaults={
                                'description': description,
                                'is_special': is_special
                            }
                        )
                        if created:
                            imported_count += 1
                            self.stdout.write(self.style.SUCCESS(f'追加: {obj}'))
                        else:
                            updated_count += 1
                            self.stdout.write(self.style.WARNING(f'更新: {obj}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"エラー: {name} - {e}"))
                        skipped_count += 1

                self.stdout.write(self.style.SUCCESS(f"--- インポート完了 ---"))
                self.stdout.write(self.style.SUCCESS(f"新規追加: {imported_count} 件"))
                self.stdout.write(self.style.SUCCESS(f"更新: {updated_count} 件"))
                self.stdout.write(self.style.WARNING(f"スキップ: {skipped_count} 件"))

        except FileNotFoundError:
            raise CommandError(f"ファイル '{csv_path}' が見つかりません。")
        except Exception as e:
            raise CommandError(f"ファイル読み込み中にエラーが発生しました: {e}")
