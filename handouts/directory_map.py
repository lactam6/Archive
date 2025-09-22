import os
import json
import re # 正規表現モジュールをインポート

def natural_sort_key(s):
    """
    ファイル名を自然順（数字を数値として比較）でソートするためのキーを生成します。
    特に '#数字_' のパターンに対応します。
    """
    if s.startswith('#') and '_' in s:
        # '#数字_' パターンを検出
        match = re.match(r'^#(\d+)_.*', s)
        if match:
            # 数字部分を整数に変換してソートキーの先頭にする
            return [int(match.group(1))] + [x.lower() for x in re.split('([0-9]+)', s)]
    
    # 通常のファイル名、またはパターンに一致しない場合は、一般的な自然順ソート
    # 数字部分を数値として、それ以外を文字列として分割
    return [int(x) if x.isdigit() else x.lower() for x in re.split('([0-9]+)', s)]


def generate_directory_map(root_folder):
    """
    指定されたルートフォルダ以下のディレクトリマップを生成します。
    各フォルダをキーとし、そのフォルダ内のPDFファイル名のリストを値とする辞書を返します。
    ファイル名は '#数字_' のパターンで自然順ソートされます。
    """
    directory_map = {}

    if not os.path.isdir(root_folder):
        print(f"エラー: 指定されたルートフォルダ '{root_folder}' が見つかりません。")
        return None

    for dirpath, dirnames, filenames in os.walk(root_folder):
        pdf_files_in_current_dir = [
            f for f in filenames if f.lower().endswith('.pdf')
        ]

        # ここでカスタムソートキーを使用してソート
        # natural_sort_key 関数に各ファイル名を渡して、ソートのための値を生成
        sorted_pdf_files = sorted(pdf_files_in_current_dir, key=natural_sort_key)


        relative_dir_path = os.path.relpath(dirpath, root_folder).replace(os.sep, '/')

        if relative_dir_path == '.':
            key_name = os.path.basename(root_folder)
        else:
            key_name = os.path.basename(root_folder) + '/' + relative_dir_path

        if sorted_pdf_files: # PDFファイルがある場合のみマップに追加
            directory_map[key_name] = sorted_pdf_files
        
    return directory_map

def save_map_to_file(data_map, output_filename, format='json'):
    """
    生成されたディレクトリマップを指定されたファイルに保存します。
    """
    if data_map is None:
        return

    output_path = os.path.join(output_filename)

    try:
        if format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data_map, f, indent=4, ensure_ascii=False)
            print(f"ディレクトリマップをJSON形式で '{output_path}' に保存しました。")
        elif format.lower() == 'txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                for folder, pdfs in data_map.items():
                    f.write(f"フォルダ: {folder}\n")
                    if pdfs:
                        for pdf in pdfs:
                            f.write(f"  - {pdf}\n")
                    else:
                        f.write("  (PDFファイルなし)\n")
                    f.write("\n")
            print(f"ディレクトリマップをTXT形式で '{output_path}' に保存しました。")
        else:
            print(f"エラー: サポートされていない出力形式 '{format}' です。'json' または 'txt' を指定してください。")
    except Exception as e:
        print(f"エラー: ファイルの保存中に問題が発生しました: {e}")

# --- スクリプトの実行部分 ---
if __name__ == "__main__":
    root_folder_path = "handouts"

    map_data = generate_directory_map(root_folder_path)

    if map_data:
        print("\n生成されたディレクトリマップ:")
        print(json.dumps(map_data, indent=4, ensure_ascii=False))

        output_file_name = os.path.join(root_folder_path, "directory_map.json")
        save_map_to_file(map_data, output_file_name, format='json')