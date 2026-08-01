# シフト表ビューア セットアップ手順

## ファイル構成

```
shift-viewer/
├── index.html                    # 表示ページ（メモ編集機能付き）
├── shifts.json                   # シフトデータ（自動更新される）
├── memos.json                    # メモデータ（ページ上で編集可能）
├── scraper.py                    # スクレイパー
└── .github/workflows/update.yml  # 自動更新（1日4回）
```

## セットアップ（約10分）

### 1. リポジトリ作成

1. GitHub にログイン → 右上「+」→「New repository」
2. Repository name: `shift-viewer`（任意の名前でOK）
3. **Public** を選択（GitHub Pages 無料利用のため）
4. 「Create repository」

### 2. ファイルアップロード

1. 「uploading an existing file」リンクをクリック
2. このZIP内の全ファイルをドラッグ&ドロップ
   - `.github` フォルダも含めて構造そのままアップロード
   - Webからアップロードできない場合は「Add file」→「Create new file」で
     ファイル名に `.github/workflows/update.yml` と入力すればフォルダごと作れます
3. 「Commit changes」

### 3. GitHub Pages 有効化

1. リポジトリの「Settings」→ 左メニュー「Pages」
2. Source: **Deploy from a branch**
3. Branch: **main** / **(root)** → Save
4. 数分後、`https://<ユーザー名>.github.io/shift-viewer/` で公開されます

### 4. Fine-grained PAT 作成（メモ編集を使う場合）

1. GitHub 右上アイコン → Settings → 最下部「Developer settings」
2. 「Personal access tokens」→「Fine-grained tokens」→「Generate new token」
3. 設定：
   - Token name: `shift-memo`
   - Expiration: 1年など長めに
   - Repository access: **Only select repositories** → `shift-viewer` を選択
   - Permissions → Repository permissions → **Contents: Read and write**
4. 「Generate token」→ 表示されたトークン（`github_pat_...`）をコピー

### 5. index.html にトークン設定

`index.html` 内の以下の部分を編集：

```javascript
const GH = {
  owner: 'YOUR_GITHUB_USERNAME',   // ← 自分のGitHubユーザー名
  repo: 'YOUR_REPO_NAME',          // ← shift-viewer
  token: '',                       // ← github_pat_xxx を貼り付け
  branch: 'main',
};
```

GitHub上で index.html を開き、鉛筆アイコン（Edit）から直接編集できます。

### 6. 自動更新の確認

1. リポジトリの「Actions」タブ
2. 「Update shifts」→「Run workflow」で手動テスト実行
3. 緑のチェックが付けば成功。以降、毎日 8時/12時/17時/21時（JST）に自動実行

## 運用

- **シフト**: 元HPが更新されると自動で反映（最大数時間のタイムラグ）
- **メモ**: ページで名前タップ → 編集 → 保存（GitHubに直接コミットされる）
- **メモをClaude経由で更新**: チャットで依頼 → 更新版 memos.json を作成

## 注意

- Public リポジトリのため、URLを知っていれば誰でも閲覧可能です
- トークンはこのリポジトリのContents書き込み権限のみなので、
  漏洩してもこのリポジトリのファイル書き換え以上の被害はありません
- 元HPの構造が変わった場合はスクレイパーの修正が必要です（チャットで依頼してください）
