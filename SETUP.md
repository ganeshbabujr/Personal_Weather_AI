# Setup

## Secrets  (Settings > Secrets and variables > Actions > Secrets)
  OWM_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID   (chat = a private chat with your bot, only you)
  GOLD_API_KEY   optional, for gold and silver rates (goldapi.io free plan is small, rates are cached once a day)

## Variables  (same page > Variables). All optional except ZIP_CODE.
  ZIP_CODE        600001,IN
  SHEET_CSV_URL   published CSV link of your family Google Sheet (see below)
  HOLIDAY_STATE   TN                     state code for state holidays
  EXTRA_ZIPS      641001,IN;110001,IN    other places family lives (semicolon separated), shown on the weather card
  SCHOOL_DROP     08:00                  adds "rain at school drop-off" tip
  SCHOOL_PICKUP   15:30                  adds "rain at school pick-up" tip
  SCHOOL_OFF      sun                    days with no school, tips are skipped (default sun; e.g. sat,sun)
  WATCH           elders,asthma,kids     adds extra personal tips for each
  WIND_LIMIT      60                     km/h for the "do not go outside" alert
  SEND_AT         06:00                  exact time the daily briefing is sent (default 06:00)
  SEND_TZ         Asia/Kolkata           time zone for SEND_AT (default Asia/Kolkata)
  BRIEF_LANG      ta                     Tamil on every card and caption (default en)
  BIG_TEXT        1                      15% bigger text, good for elders

## Family Google Sheet
Columns (first row): name, date, type, repeat, year, day, wish, photo
  type    birthday | anniversary | bill | temple | reminder | event
  repeat  yearly | monthly | bimonthly_odd | bimonthly_even | daily (leave empty for a one-time date)
  date    2026-11-15 (one time) or 11-15 (yearly)       day  1-31 for monthly bills
  year    birth / wedding year, to show "turns 12" or "(30 years)"
  wish    optional personal birthday wish (shown on the birthday card)
  photo   optional: photos/priya.jpg in the repo, or leave empty (see below)
Birthday photos: add a folder `photos/` to the repo and save the picture as `photos/<name>.jpg`
in lowercase (priya.jpg, first-last.jpg for two words). It is used automatically.
Then File > Share > Publish to web > CSV, and put that link in SHEET_CSV_URL.

## What gets sent
Daily at SEND_AT (6:00 AM IST): the workflow starts about an hour early (GitHub schedules are never exact) and the script waits for the exact time. ONE album message with Weather, Panchangam and Events cards (plus a
Week-ahead card on Sundays). The key facts are also in the caption text under the first card.
Birthdays get their own card. Storm Watch checks every hour (6:42 AM - 10:12 PM IST) and sends each alert once. It only installs a browser when a rain card has to be sent, which keeps GitHub minutes low on a private repo (free plan: 2,000 minutes a month).

## Test
Actions tab > Daily Family Briefing > Run workflow. Cards are also saved as an artifact for 3 days.
If a run fails you get a Telegram message with a link to the run.

## Exact timing (cron-job.org)
GitHub's own schedule ran 4-5 hours late, so the workflows no longer use it. A free cron-job.org account
starts them instead. Make two jobs, both POST, time zone Asia/Kolkata, with headers
  Authorization: Bearer <fine-grained token, repo access only, Actions: read and write>
  Accept: application/vnd.github+json
  Content-Type: application/json
and body {"ref":"main"}
  Daily briefing  URL .../actions/workflows/weather.yml/dispatches   crontab  58 5 * * *
  Storm watch     URL .../actions/workflows/watch.yml/dispatches     crontab  12 6-22 * * *
Turn on "execution of the cronjob fails" so you get an email if it stops working.
The token expires (check its page in GitHub > Settings > Developer settings); make a new one before then.
