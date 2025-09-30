import os
import json
import re

def sort_files_by_name(files):
    """
    ファイル名のソートロジックを適用してファイルを並び替える関数。

    Args:
        files (list): ファイル名のリスト。

    Returns:
        list: ソートされたファイル名のリスト。
    """
    def sort_key(filename):
        # ファイル名の最初にシャープ"#"が含まれる場合
        if filename.startswith('#'):
            match = re.match(r'#(\d+)', filename)
            if match:
                return (0, int(match.group(1))) # 優先順位 0, 数字でソート

        # ファイル名の最後に数字が含まれる場合
        match = re.search(r'(\d+)\.pdf$', filename, re.IGNORECASE)
        if match:
            return (1, int(match.group(1))) # 優先順位 1, 数字でソート

        # 上記のルールに当てはまらない場合
        return (2, filename) # 優先順位 2, 通常のファイル名でソート

    return sorted(files, key=sort_key)

def get_pdf_directory_structure(root_path):
    """
    指定されたフォルダ下のすべてのPDFファイルのディレクトリ構造を、
    階層的なツリー構造のJSON形式で取得する関数。
    
    Args:
        root_path (str): 探索を開始するフォルダのパス。

    Returns:
        dict: フォルダ構造を表す辞書。エラーの場合はNone。
    """
    if not os.path.isdir(root_path):
        print(f"エラー: 指定されたパス '{root_path}' は有効なディレクトリではありません。")
        return None

    tree = {
        "name": os.path.basename(root_path) or "root",
        "type": "directory",
        "children": []
    }
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        
        # PDFファイルのみを抽出し、並び替える
        pdf_files = [f for f in filenames if f.lower().endswith('.pdf')]
        sorted_pdf_files = sort_files_by_name(pdf_files)
        
        path_parts = os.path.relpath(dirpath, root_path).split(os.sep)

        current_node = tree
        if path_parts != ['.']:
            for part in path_parts:
                for child in current_node["children"]:
                    if child["name"] == part and child["type"] == "directory":
                        current_node = child
                        break
        
        # サブディレクトリは名前順にソートして追加
        for dirname in sorted(dirnames):
            dir_node = {
                "name": dirname,
                "type": "directory",
                "children": []
            }
            current_node["children"].append(dir_node)

        # 並び替えられたPDFファイルをノードとして追加
        for filename in sorted_pdf_files:
            file_path = os.path.join(dirpath, filename)
            file_size = os.path.getsize(file_path)
            
            file_node = {
                "name": filename,
                "type": "file",
                "extension": "pdf",
                "size_bytes": file_size
            }
            current_node["children"].append(file_node)
                
    return tree

# --- 使用例 ---
if __name__ == "__main__":
    folder_to_scan = 'handouts'
    
    # テスト用のフォルダとファイルを準備
    if not os.path.exists(folder_to_scan):
        os.makedirs(os.path.join(folder_to_scan, "archive"))
        with open(os.path.join(folder_to_scan, "file_10.pdf"), "w") as f: f.write("dummy")
        with open(os.path.join(folder_to_scan, "#1_report.pdf"), "w") as f: f.write("dummy")
        with open(os.path.join(folder_to_scan, "#2.pdf"), "w") as f: f.write("dummy")
        with open(os.path.join(folder_to_scan, "appendix_2.pdf"), "w") as f: f.write("dummy")
        with open(os.path.join(folder_to_scan, "archive", "#10_notes.pdf"), "w") as f: f.write("dummy")
        with open(os.path.join(folder_to_scan, "archive", "summary_5.pdf"), "w") as f: f.write("dummy")
        with open(os.path.join(folder_to_scan, "normal_file.pdf"), "w") as f: f.write("dummy")

    pdf_structure = get_pdf_directory_structure(folder_to_scan)

    if pdf_structure:
        output_filename = "handouts_structure.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(pdf_structure, f, indent=2, ensure_ascii=False)
        print(f"PDFのフォルダ構造が '{output_filename}' に保存されました。")
        
        print("\n--- 取得されたJSON構造 ---")
        print(json.dumps(pdf_structure, indent=2, ensure_ascii=False))