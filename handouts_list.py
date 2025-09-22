import os
import json
def read_subjects_to_list(filepath="subjects.txt"):
    """
    指定されたファイルパスのファイルを読み込み、各行をリストの要素として返します。

    Args:
        filepath (str): 読み込むファイルのパス。デフォルトは "subjects.txt" です。

    Returns:
        list: ファイルの各行を含む文字列のリスト。
              ファイルが見つからない場合は空のリストを返します。
    """
    lines = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                # 各行の末尾にある改行文字（\n）を削除します
                lines.append(line.strip())
    except FileNotFoundError:
        print(f"エラー: ファイル '{filepath}' が見つかりませんでした。")
    except Exception as e:
        print(f"ファイルの読み込み中にエラーが発生しました: {e}")
    return lines

def generate_markdown_from_map(map_file_path, output_md_path, handouts_root_name="handouts"):
    """
    ディレクトリマップ (JSON) を読み込み、指定された形式のMarkdownファイルを生成します。

    Args:
        map_file_path (str): directory_map.json ファイルへのパス。
        output_md_path (str): 生成するMarkdownファイルの出力パス。
        handouts_root_name (str): マップのキーの先頭に付くルートフォルダ名（例: "handouts"）。
    """
    if not os.path.exists(map_file_path):
        print(f"エラー: ディレクトリマップファイル '{map_file_path}' が見つかりません。")
        return

    try:
        with open(map_file_path, 'r', encoding='utf-8') as f:
            directory_map = json.load(f)
    except json.JSONDecodeError as e:
        print(f"エラー: JSONファイルの読み込みに失敗しました。ファイルが破損している可能性があります: {e}")
        return
    except Exception as e:
        print(f"エラー: ファイルの読み込み中に問題が発生しました: {e}")
        return

    # 出力ディレクトリが存在しない場合は作成
    output_dir = os.path.dirname(output_md_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    try:
        with open(output_md_path, 'w', encoding='utf-8') as f:
            # 何も書き込まないので、ファイルの内容は空になります。
            pass
    except Exception as e:
        print(f"ファイルの消去中にエラーが発生しました: {e}")
    with open(output_md_path, 'a', encoding='utf-8') as md_file:
        # 辞書のキー（フォルダパス）をソートして出力順を制御
        # 'handouts' -> 'handouts/chapter1' -> 'handouts/chapter2' のようにソート
        sorted_folders = sorted(directory_map.keys())

        for folder_key in sorted_folders:
            pdf_files = directory_map[folder_key]

            # ディレクトリの表示名を作成 (例: handouts/2025年生化学1)
            # 'handouts' キーの場合はそのまま 'handouts' と表示するか、特別な名前にする
            if folder_key == handouts_root_name:
                display_folder_name = f"{handouts_root_name} (ルート)" # または単に handouts_root_name
            else:
                display_folder_name = folder_key # 'handouts/2025年生化学1' のような形式

            md_file.write(f"## {display_folder_name}\n")
            md_file.write("---\n") # 水平線を追加

            if pdf_files:
                for pdf_file in pdf_files:
                    # PDFファイルのフルパスを作成 (例: handouts/2025年生化学1/#1_オリエンテーション.pdf)
                    # os.path.join はOSごとのパス区切り文字を使うため、
                    # MarkdownリンクのURLパス形式に合わせて '/' に置き換える
                    
                    # リンクの表示テキスト (例: #1_オリエンテーション)
                    link_text = os.path.splitext(pdf_file)[0] # 拡張子を除去
                    
                    # リンクのターゲットパス (例: ./handouts/2025年生化学1/#1_オリエンテーション.pdf)
                    # directory_mapのキー (folder_key) は既に "handouts/folder" の形式なので、それにファイル名を結合
                    pdf_relative_path = f"./{folder_key}/{pdf_file}" # 相対パス形式のURL

                    # Markdownリンクの生成
                    md_file.write(f"[{link_text}]({pdf_relative_path})\n")
            else:
                md_file.write("_(このフォルダにはPDFファイルがありません。)_\n")
            
            md_file.write("\n") # 各セクションの後に空行

    print(f"Markdownファイル '{output_md_path}' を生成しました。")

# --- スクリプトの実行部分 ---
if __name__ == "__main__":
    subject_list = read_subjects_to_list("subjects.txt")
    output_markdown_file = "index.md" 
    for subject in subject_list:
        map_file = os.path.join(subject, "directory_map.json")
        generate_markdown_from_map(map_file, output_markdown_file)