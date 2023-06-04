# チャッ君＠Slack

## ローカルでの起動方法

### .envファイルの作成

.env.sampleファイルから.envファイルを作成し、SlackのAPIキーなどを設定する。

```
cp .env.sample .env
```

### Dockerイメージの作成と起動

```
docker build -t chatkun .
docker run -p 8080:8080 --env-file .env chatkun
ngrok http 8080
```

## デプロイ方法

### 環境変数の設定

```
cat .env | while read line || [[ -n "$line" ]]; do flyctl secrets set "${line?}"; done
```

### デプロイ

```
fly deploy --detach
```