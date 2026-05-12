from bs4 import BeautifulSoup

# Function to extract usernames from the HTML file
def extract_usernames_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    usernames = []

    # Find all <a> tags with href containing the Instagram URL pattern
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if "https://www.instagram.com/_u/" in href:
            # Extract the username from the URL
            username = href.split("https://www.instagram.com/_u/")[1].split('/')[0]
            usernames.append(username)
        elif "https://www.instagram.com/" in href:
            # Extract the username from the text inside the <a> tag
            username = a_tag.text.strip()
            usernames.append(username)

    return usernames

def format_list(title, items):
    if not items:
        return f"{title}: None"
    formatted = [f"{idx + 1}. {item}" for idx, item in enumerate(items)]
    return f"{title}:\n" + "\n".join(formatted)

# File paths for followers and followings
followers_file = "followers_1.html"#r"C:\OtherStuff\Random\connections\followers_and_following\followers_1.html"  # Replace with the actual path to your followers file
followings_file = "following.html"# r"C:\OtherStuff\Random\connections\followers_and_following\followings.html"  # Replace with the actual path to your followings file

# Extract usernames from the HTML files
followers = extract_usernames_from_html(followers_file)
followings = extract_usernames_from_html(followings_file)

print("Amount of followers:", len(followers))
print("Amount of followings:", len(followings))

# Find the two requested lists
not_followed_back = [user for user in followers if user not in followings]
not_following_back = [user for user in followings if user not in followers]

print("Amount of People not followed back:", len(not_followed_back))
print("Amount of People not following back:", len(not_following_back))

# Output the results
print(format_list("People who follow me, but I do not follow them:", not_followed_back))
print(format_list("People who don't follow me, but I follow them:", not_following_back))
