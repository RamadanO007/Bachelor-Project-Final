email_start_times = [
    1723044461,
    1723044741,
    1723044908,
    1723045137,
    1723045309,
    1723045448,
    1723045590,
    1723045824,
    1723045961,
    1723046111,
    1723046433,
    1723046571,
]

email_end_times = [
    1723044536,
    1723044778,
    1723045024,
    1723045217,
    1723045366,
    1723045517,
    1723045722,
    1723045900,
    1723046029,
    1723046302,
    1723046531,
    1723046661,
]











# Calculate the time spent on each email
email_times = [end - start for start, end in zip(email_start_times, email_end_times)]

# Calculate the gaps between the end of one email and the start of the next
gaps = []
for i in range(len(email_start_times) - 1):
    gap = email_start_times[i + 1] - email_end_times[i]
    if gap < 10:
        gaps.append(f"{gap} seconds - ERROR")
    else:
        gaps.append(f"{gap} s")


print("Email Times:", email_times)
print("Gaps", gaps)
