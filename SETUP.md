# Setup

Secrets (Settings > Secrets and variables > Actions > Secrets):
  OWM_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID   (chat = a private chat with your bot, only you)

Variables (same page > Variables). All optional except ZIP_CODE:
  ZIP_CODE        600001,IN
  HOLIDAY_STATE   TN                    state code for state holidays
  EXTRA_ZIPS      641001,IN;110001,IN   other places family lives (semicolon separated)
  SCHOOL_DROP     08:00                 rain-at-school-time tip
  SCHOOL_PICKUP   15:30
  WATCH           elders,asthma,kids    extra personal tips
  WIND_LIMIT      60                    km/h for the DO NOT GO OUTSIDE alert

Test: Actions tab > Daily Family Briefing > Run workflow. The card is also saved
as an artifact for 3 days. Edit events.yaml to add birthdays, bills and reminders.
