#import_exercises.py
import csv
from django.core.management.base import BaseCommand, CommandError
from exercise.models import Exercise, LEVEL_CHOICES  # exerciseアプリのmodelsからExerciseモデルをインポート

class Command(BaseCommand):
    help = 'CSVファイルから運動データをインポートします。'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='インポートするCSVファイルのパス')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                imported_count = 0
                updated_count = 0
                skipped_count = 0

                for row in reader:
                    exercise_name_full = row.get('exercise')
                    level_str = row.get('level')

                    if not exercise_name_full or not level_str:
                        self.stdout.write(self.style.WARNING(f"スキップ: 運動名またはレベル不足 - {row}"))
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

                    try:
                        exercise, created = Exercise.objects.update_or_create(
                            name=exercise_name_full,
                            defaults={'level': level}
                        )
                        if created:
                            imported_count += 1
                            self.stdout.write(self.style.SUCCESS(f"インポート: {exercise_name_full} (レベル: {level})"))
                        else:
                            updated_count += 1
                            self.stdout.write(self.style.SUCCESS(f"更新: {exercise_name_full} (レベル: {level})"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"エラー: {exercise_name_full} - {e}"))
                        skipped_count += 1

                self.stdout.write(self.style.SUCCESS(f"--- インポート完了 ---"))
                self.stdout.write(self.style.SUCCESS(f"新規インポート: {imported_count} 件"))
                self.stdout.write(self.style.SUCCESS(f"更新: {updated_count} 件"))
                self.stdout.write(self.style.WARNING(f"スキップ: {skipped_count} 件"))

        except FileNotFoundError:
            raise CommandError(f"ファイル '{csv_file_path}' が見つかりません。")
        except Exception as e:
            raise CommandError(f"ファイル読み込み中にエラーが発生しました: {e}")