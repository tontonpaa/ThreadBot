#main.py
import os
import discord
from dotenv import load_dotenv
import asyncio

load_dotenv()

TOKEN = os.environ['DISCORD_TOKEN']

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def update_presence():
    """Botのステータスを定期的に更新する"""
    while True:
        ping = round(client.latency * 1000)
        activity_ping = discord.Game(name=f"Ping: {ping}ms")
        await client.change_presence(activity=activity_ping)
        await asyncio.sleep(5)  # 5秒ごとに更新

        guild_count = len(client.guilds)
        activity_servers = discord.Game(name=f"サーバー数: {guild_count}")
        await client.change_presence(activity=activity_servers)
        await asyncio.sleep(5)  # さらに5秒後に切り替え

async def unarchive_thread(thread: discord.Thread):
    """スレッドがアーカイブされていた場合に解除する"""
    if thread.archived:
        try:
            await thread.edit(archived=False)
            print(f"スレッド '{thread.name}' のアーカイブを解除しました。")
        except discord.errors.NotFound:
            print(f"スレッド '{thread.name}' は見つかりませんでした。")
        except discord.errors.Forbidden:
            print(f"スレッド '{thread.name}' のアーカイブを解除する権限がありません。")
        except Exception as e:
            print(f"スレッド '{thread.name}' のアーカイブ解除中にエラーが発生しました: {e}")

@client.event
async def on_thread_update(before, after):
    """スレッドの状態が更新された際に実行される"""
    if before.archived and not after.archived:
        # アーカイブ解除されたスレッドはここでは処理しない (無限ループ防止)
        return

    if not before.archived and after.archived and after.me:
        # Bot自身が作成したスレッドがアーカイブされた場合、即座にアーカイブ解除を試みる
        await unarchive_thread(after)

@client.event
async def on_message(message):
    print(f"on_message イベントが発生しました。")
    print(f"message.author: {message.author}")
    print(f"message.channel の型: {type(message.channel)}")
    print(f"message.channel: {message.channel}")
    print(f"message.type: {message.type}")
    print(f"message.content の値 (raw): '{message.content}'")

    if message.content == "テスト":
        await message.add_reaction("👍")
        return

    # テキストチャンネルかつ通常のメッセージの場合に処理
    if isinstance(message.channel, discord.channel.TextChannel) and message.type == discord.MessageType.default:
        if message.content:
            # ここで再度 content を確認
            print(f"message.content (処理直前): '{message.content}'")
            thread_name = message.content[:100].strip()  # 先頭100文字を取得し、前後の空白を削除
            print(f"thread_name (処理後): '{thread_name}'")

            try:
                # メッセージの内容の先頭100文字（トリム後）をスレッド名に設定
                thread = await message.create_thread(name=thread_name, auto_archive_duration=10080)
                print(f"スレッドを作成しました。スレッド名: '{thread.name}'")
                # await thread.leave()
            except discord.errors.Forbidden as e:
                print(f"スレッド作成中に権限エラーが発生しました: {e}")
            except discord.errors.HTTPException as e:
                print(f"スレッド作成中に HTTP エラーが発生しました: {e}")
            except Exception as e:
                print(f"スレッド作成中に予期せぬエラーが発生しました: {e}")
        else:
            print("メッセージ内容が空のため、スレッド作成をスキップします。")

@client.event
async def on_message_delete(message):
    """メッセージが削除された際に実行される"""
    # Botが送信したスレッド作成時の自動メッセージを検出して削除
    if message.author == client.user and message.content.endswith("すべてのスレッドを見る場合はこちら。"):
        try:
            await message.delete()
            print(f"自動メッセージ '{message.content}' を削除しました。")
        except discord.errors.NotFound:
            print("削除しようとしたメッセージは見つかりませんでした。")
        except discord.errors.Forbidden:
            print("メッセージを削除する権限がありません。")
        except Exception as e:
            print(f"自動メッセージの削除中にエラーが発生しました: {e}")

@client.event
async def on_ready():
    print("discord.py v" + discord.__version__)
    print("Bot は準備完了です！")
    client.loop.create_task(update_presence())

client.run(str(TOKEN))