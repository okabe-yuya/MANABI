from github import Github
from datetime import datetime, timedelta, timezone
import os

REPO_NAME = os.environ["REPO"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
repo = Github(GITHUB_TOKEN).get_repo(REPO_NAME)

JST = timezone(timedelta(hours=9))
now = datetime.utcnow()
review_days = [1, 2, 5, 7, 14, 31, 90, 180, 365]

for day in review_days:
        target = []
        for issue in repo.get_issues(state="open"):
            if issue.pull_request is not None:
                continue
            
            # ラベルに '復習' が含まれているかチェック
            label_names = [label.name for label in issue.labels]
            if "復習" in label_names:
                continue  # すでに復習系Issueならスキップ

            created_at_jst = issue.created_at.astimezone(JST)
            days_ago = (now.date() - created_at_jst.date()).days
            if days_ago == day:
                    target.append(issue)

        if not target:
            continue

        body_lines = [
            f"このIssueは作成してから**{day}日後** の復習対象です。",
            "",
            "以下のIssueを確認してください:",
            "",
        ]
        for issue in target:
            body_lines.append(f"- [ ] [#{issue.number} {issue.title}](https://github.com/{REPO_NAME}/issues/{issue.number})")

        body = "\n".join(body_lines)

        title = f"📚 {day}日後の復習リスト ({now.strftime('%Y-%m-%d')})"
        repo.create_issue(title=title, body=body, labels=["復習"])

