import tempfile

import click
import requests


@click.command()
@click.option(
    "--slack_token",
    prompt="Slack token for app/bot",
    help="See OAuth and Permissions in app details at https://api.slack.com/apps/",
)
@click.option(
    "--rc_url", prompt="Rocket.Chat instance", default="https://chat.ratchet.express"
)
@click.option(
    "--rc_user",
    prompt="Rocket.Chat username",
    help="User must be able to add emoji",
)
@click.option("--rc_pass", prompt="Rocket.Chat password")
def import_emoji(slack_token, rc_url, rc_user, rc_pass):
    slack_emoji = get_slack_emoji(slack_token)

    print("Found {:d} emoji in Slack".format(len(slack_emoji)))

    rc_token, rc_userid = auth_rc(rc_url, rc_user, rc_pass)
    upload_count = 0

    for macro, item in slack_emoji.items():
        if not item.startswith("https://"):
            continue

        if create_rc_emoji(rc_url, rc_token, rc_userid, macro, item):
            upload_count += 1
        else:
            print("Failed to create emoji {}".format(macro))

    print("Created {:d} emoji in Rocket.Chat".format(upload_count))


def get_slack_emoji(slack_token):
    req = requests.get(
        "https://slack.com/api/emoji.list",
        headers={"Authorization": "Bearer {}".format(slack_token)},
    )
    req.raise_for_status()
    data = req.json()
    return data["emoji"]


def auth_rc(rc_url, rc_user, rc_pass):
    req = requests.post(
        "{}/api/v1/login".format(rc_url), data={"user": rc_user, "password": rc_pass}
    )
    req.raise_for_status()
    data = req.json()
    return data["data"]["authToken"], data["data"]["userId"]


def create_rc_emoji(rc_url, rc_token, rc_userid, macro, url):
    image_data = requests.get(url, stream=True)
    print("Attempting to create emoji :{}: from URL: {}".format(macro, url))

    with tempfile.TemporaryFile() as fd:
        for chunk in image_data.iter_content(chunk_size=128):
            fd.write(chunk)

        fd.seek(0)

        req = requests.post(
            "{}/api/v1/emoji-custom.create".format(rc_url),
            headers={
                "X-Auth-Token": rc_token,
                "X-User-Id": rc_userid,
            },
            data={"name": macro},
            files={"emoji": fd},
        )

        if req.status_code == 400:
            print("Invalid request - likely due to emoji already existing")
            return False

        req.raise_for_status()

        resp = req.json()
        print(resp)
        return resp["success"]


if __name__ == "__main__":
    import_emoji()
