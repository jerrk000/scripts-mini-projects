# Import libraries
import re
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# --- Load chat file ---
with open("WhatsApp-Chat_with_person.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# --- Regex for my file format ---
pattern = re.compile(r"^(\d{1,2}\.\d{1,2}\.\d{2,4}), (\d{1,2}:\d{2}) - (.*?): (.*)")

messages = []
current_message = None

for line in lines:
    line = line.strip()
    if not line:
        continue

    match = pattern.match(line)
    if match:
        # New message line
        if current_message:
            messages.append(current_message)
        date_str, time_str, sender, message = match.groups()
        datetime_str = f"{date_str} {time_str}"
        current_message = [datetime_str, sender.strip(), message.strip()]
    else:
        # Continuation of previous message
        if current_message:
            current_message[2] += " " + line

# Add last message
if current_message:
    messages.append(current_message)

df = pd.DataFrame(messages, columns=["datetime_str", "sender", "message"])

# --- Parse datetime ---
df["datetime"] = pd.to_datetime(df["datetime_str"], format="%d.%m.%y %H:%M", errors="coerce")

print(df.head())

# --- Compute metrics ---
df["msg_length"] = df["message"].apply(len)
df["question_marks"] = df["message"].str.count(r"\?")

avg_length = df.groupby("sender")["msg_length"].mean()
avg_questions = df.groupby("sender")["question_marks"].mean()

# --- Response time computation ---
df["next_sender"] = df["sender"].shift(-1)
df["next_time"] = df["datetime"].shift(-1)
df["response_time"] = (df["next_time"] - df["datetime"]).dt.total_seconds() / 60

responses = df[df["sender"] != df["next_sender"]]
avg_response_time = responses.groupby("next_sender")["response_time"].mean()

# --- Count messages per person ---
message_counts = df["sender"].value_counts()

# Sort by datetime
df = df.sort_values("datetime")
# Calculate time gaps
df["time_gap"] = (df["datetime"] - df["datetime"].shift(1)).dt.total_seconds() / 60
# Find longest gap
idx = df["time_gap"].idxmax()
longest_gap = df.loc[idx, "time_gap"]
last_message_time = df.loc[idx - 1, "datetime"]
last_message_sender = df.loc[idx - 1, "sender"]


# --- Display results ---
print("\nNumber of messages sent per person:\n", message_counts.to_string(index=True, header=False))
print("\nAverage message length:\n", avg_length.to_string(index=True, header=False))
print("\nAverage response time (minutes):\n", avg_response_time.to_string(index=True, header=False))
#print("\nAverage question marks per message:\n", avg_questions.to_string(index=True, header=False))
print(f"\nLongest period without messages: {longest_gap:.1f} minutes")
print(f"Last message before this gap was from: {last_message_sender} at {last_message_time}")

############ Histogram of response times ###############

# Only include when sender changes
responses = df[df["sender"] != df["next_sender"]].dropna(subset=["response_time"])

# --- Define 10-minute bins up to the 95th percentile (ignore extreme outliers) ---
max_time = responses["response_time"].quantile(0.95)
bins = np.arange(0, max_time + 10, 10)

# --- Plot ---
plt.figure(figsize=(9,5))

senders = list(responses["next_sender"].unique())

# Step-outline histogram for the first person
plt.hist(
    responses[responses["next_sender"] == senders[0]]["response_time"],
    bins=bins,
    histtype="step",
    linewidth=2,
    label=senders[0],
    color="darkorange"
)

# Filled histogram for everyone else
for sender in senders[1:]:
    plt.hist(
        responses[responses["next_sender"] == sender]["response_time"],
        bins=bins,
        alpha=0.6,
        label=sender,
        color="skyblue",
        edgecolor="black"
    )


plt.xlabel("Response time (minutes)")
plt.ylabel("Frequency")
plt.title("Histogram of Response Times per Person")
plt.legend()
plt.tight_layout()
plt.show()

# Activity per hour of the day

# Extract hour of day
df["hour"] = df["datetime"].dt.hour

plt.figure(figsize=(10,5))

# Get unique senders
senders = df["sender"].unique()

# First person: normal filled histogram
plt.hist(
    df[df["sender"] == senders[0]]["hour"],
    bins=range(0,25),
    alpha=0.6,
    label=senders[0],
    color="skyblue",
    edgecolor="black"
)

# Second person: step outline histogram for contrast
if len(senders) > 1:
    plt.hist(
        df[df["sender"] == senders[1]]["hour"],
        bins=range(0,25),
        histtype="step",
        linewidth=2,
        label=senders[1],
        color="darkorange"
    )

plt.xticks(range(0,24))
plt.xlabel("Hour of Day")
plt.ylabel("Number of Messages")
plt.title("Messages per Hour of the Day (per Person)")
plt.legend()
plt.tight_layout()
plt.show()