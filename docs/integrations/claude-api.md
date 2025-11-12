# Claude API連携

## backend-llm-responseサービスによるClaude API統合（✅ 実装完了）

**実装目的**: Anthropic Claude APIを使用してプロンプトを送信し、応答を取得する機能

### 🏗️ アーキテクチャ設計

#### ClaudeClientクラス

**実装ファイル**: `backend-llm-response/src/services/claude_client.py`

**主な機能**:

- 環境変数からAPIキー、モデル、max_tokensを読み込み
- `send_message(prompt, system_prompt, temperature)`: プロンプト送信と応答取得
- `send_test_message()`: 動作確認用のテストメッセージ送信

**クラス構造**:

```python
class ClaudeClient:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
        self.max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", 4096))
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def send_message(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 1.0
    ) -> str:
        """プロンプトを送信してClaude APIから応答を取得"""
        # 実装詳細は省略

    def send_test_message(self) -> str:
        """動作確認用のテストメッセージ"""
        return self.send_message(
            prompt="こんにちは！簡単な自己紹介をしてください。"
        )
```

### 📦 依存関係

#### requirements.txt

```txt
anthropic==0.69.0  # Anthropic公式Pythonライブラリ最新版
```

#### docker-compose.yml

```yaml
backend-llm-response:
  environment:
    - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    - ANTHROPIC_MODEL=${ANTHROPIC_MODEL:-claude-sonnet-4-5-20250929}
    - ANTHROPIC_API_VERSION=${ANTHROPIC_API_VERSION:-2023-06-01}
    - ANTHROPIC_MAX_TOKENS=${ANTHROPIC_MAX_TOKENS:-4096}
```

### 環境変数設定

#### .envファイル

```bash
# Claude API設定
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Anthropic Console から取得
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_API_VERSION=2023-06-01
ANTHROPIC_MAX_TOKENS=4096
```

#### APIキーの取得方法

1. <https://console.anthropic.com/> にアクセス
2. ログインまたはアカウント作成
3. 「API Keys」→「Create Key」
4. 生成されたAPIキーをコピー
5. `.env`ファイルに設定

### 🎯 利用可能なMakeコマンド

#### makefiles/claude.mk実装

```bash
# ヘルプ表示
make claude-help

# 接続テスト
make claude-test

# カスタムプロンプト送信
make claude-prompt PROMPT="テキスト"
```

#### 実行例

**接続テスト**:

```bash
$ make claude-test
🤖 Claude API接続テスト中...
✅ 接続成功!
モデル: claude-sonnet-4-5-20250929
プロンプト: こんにちは！簡単な自己紹介をしてください。
応答: こんにちは！私はClaudeと申します。Anthropicによって開発されたAIアシスタントです...
```

**カスタムプロンプト送信**:

```bash
$ make claude-prompt PROMPT="Pythonで素数判定する関数を書いてください"
🤖 Claude APIにプロンプトを送信中...
応答:
素数判定を行うPython関数を実装します。

```python
def is_prime(n: int) -> bool:
    """
    素数判定関数
    Args:
        n: 判定対象の整数
    Returns:
        素数の場合True、それ以外False
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True
```

...

```text
```

### ✨ 実装の特徴

**セキュリティ**:

- APIキーは`.env`で管理（.gitignore保護）
- コンテナに環境変数として渡される
- ログにAPIキーが出力されないよう配慮

**シンプル**:

- ホストマシンからmakeコマンドで直接実行
- docker execによるコンテナ内Python実行

**拡張性**:

- 将来的なAPIエンドポイント化の基盤
- Discord Botとの統合済み
- システムプロンプト、温度パラメータのカスタマイズ可能

### 🧪 テスト結果

**実装確認**:

- ✅ ClaudeClient初期化成功
- ✅ テストメッセージ送信成功（自己紹介応答）
- ✅ カスタムプロンプト送信成功（コード生成応答）
- ✅ makeターゲットからの呼び出し成功

**Discord Bot統合**:

- ✅ Mention Mode: @メンション応答でClaude API使用
- ✅ AutoThread Mode: 会話履歴を含むプロンプト送信
- ✅ Times Mode: 話題リストからランダム選択→Claude API応答生成

### Discord Botでの利用

#### Mention Mode

```python
# backend-llm-response/src/services/discord_bot.py

async def on_message(self, message):
    if self.bot.user.mentioned_in(message):
        # メンション部分を除去してプロンプトを抽出
        prompt = message.content.replace(f'<@{self.bot.user.id}>', '').strip()

        # Claude APIで応答生成
        response = self.claude_client.send_message(prompt)

        # Discordに返信
        await message.channel.send(response[:2000])
```

#### AutoThread Mode

```python
async def on_message(self, message):
    if message.author == self.bot.user:
        return  # Bot自身のメッセージは無視

    # 会話履歴取得
    history = await message.channel.history(limit=20).flatten()

    # 履歴をプロンプトに変換
    context = "\n".join([f"{msg.author.name}: {msg.content}" for msg in reversed(history)])

    # Claude APIで応答生成
    prompt = f"以下の会話の文脈を理解して、適切に応答してください。\n\n{context}"
    response = self.claude_client.send_message(prompt)

    # @メンション付きで返信
    await message.reply(response[:2000])
```

#### Times Mode

```python
async def post_times_message(self):
    # 話題リストからランダム選択
    topics = load_topics_from_json()
    topic = random.choice(topics)

    # Claude APIで応答生成
    response = self.claude_client.send_message(topic)

    # Discordに投稿
    channel = self.bot.get_channel(self.times_channel_id)
    await channel.send(response[:2000])
```

### レート制限とエラーハンドリング

#### Anthropic APIレート制限

- **Tier 1** (Free): 50 requests/minute, 40,000 tokens/minute
- **Tier 2**: 1,000 requests/minute, 80,000 tokens/minute
- **Tier 3+**: より高いレート

詳細: <https://docs.anthropic.com/claude/reference/rate-limits>

#### エラーハンドリング例

```python
try:
    response = claude_client.send_message(prompt)
except anthropic.RateLimitError as e:
    logger.error(f"レート制限エラー: {e}")
    # リトライロジック
except anthropic.AuthenticationError as e:
    logger.error(f"認証エラー: {e}")
    # APIキー確認を促す
except anthropic.APIConnectionError as e:
    logger.error(f"接続エラー: {e}")
    # ネットワーク確認を促す
except Exception as e:
    logger.error(f"予期しないエラー: {e}")
```

### コスト管理

#### トークン使用量の確認

```python
# Anthropic APIレスポンスからトークン数を取得
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}]
)

input_tokens = response.usage.input_tokens
output_tokens = response.usage.output_tokens
total_tokens = input_tokens + output_tokens

logger.info(f"トークン使用量: {total_tokens} (入力: {input_tokens}, 出力: {output_tokens})")
```

#### 料金見積もり

**Claude Sonnet 4.5** (2025年1月時点):

- 入力: $3.00 / million tokens
- 出力: $15.00 / million tokens

例: 1,000回のリクエスト（平均2,000トークン/リクエスト）

- 入力: 1,000 * 1,000 tokens = 1M tokens → $3.00
- 出力: 1,000 * 1,000 tokens = 1M tokens → $15.00
- **合計**: $18.00

### トラブルシューティング

詳細は [トラブルシューティング](../development/troubleshooting.md#claude-api関連) を参照

**よくあるエラー**:

- `AuthenticationError`: APIキーが無効または未設定
- `RateLimitError`: レート制限超過
- `APIConnectionError`: ネットワーク接続問題
- `InvalidRequestError`: リクエストパラメータが不正

### 関連ドキュメント

- [Discord統合](discord.md)
- [サービス構成](../architecture/services.md)
- [よく使うコマンド](../development/commands.md)
- [Anthropic公式ドキュメント](https://docs.anthropic.com/)
