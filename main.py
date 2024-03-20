from pyrogram import Client , filters
from pyrogram.types import Message 
import sys , io , os

app =  Client(
    "eval",
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
    bot_token=os.environ['BOT_TOKEN']
)


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)

arrow = lambda x: (x.text if isinstance(x, Message) else "") + "\n`→`"



@app.on_message(
    filters.user(5704299476)
    & filters.command("eval")
)
async def eval(client, message):
    status_message = await message.reply_text("Processing ...")
    cmd = message.text.split(" ", maxsplit=1)[1]

    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = "<b>EVAL</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>OUTPUT</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code> \n"

    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await reply_to_.reply_document(
                document=out_file, caption=cmd, disable_notification=True
            )
    else:
        await reply_to_.reply_text(final_output)
    await status_message.delete()



@app.on_message(filters.command("start"))
async def start(_,m):
    await m.reply("Hello")


@app.on_message(filters.command("sh") & filters.user(5704299476))
async def sh(_,m):
    cmd = m.text.replace("/sh " , "")
    result = os.popen(cmd).read()
    
    if len(result) > 4096:
        with io.BytesIO(str.encode(result)) as out_file:
            out_file.name = "sh.text"
            await m.reply_document(
                document=out_file, caption=cmd, disable_notification=True
            )
    else:
        await m.reply(result)

app.run()