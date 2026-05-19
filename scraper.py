import requests
from bs4 import BeautifulSoup
import os

DATA_DIR = "data"

def scrape_to_txt(url, filename, section_name=None):
    """
    Scrapes text content from a webpage and appends it into data/filename.
    Adds a section header if provided.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {url} (status {response.status_code})")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        content = "\n".join(paragraphs)

        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "a", encoding="utf-8") as f:
            if section_name:
                f.write(f"\n--- {section_name} ---\n")
            f.write(f"Content from {url}\n")
            f.write(content)
            f.write("\n")

        print(f"Saved {url} → {filepath}")
    except Exception as e:
        print(f"Error scraping {url}: {e}")

if __name__ == "__main__":
    #     # --- Professional Persona ---
    # scrape_to_txt("https://bmcmededuc.biomedcentral.com/articles/10.1186/s12909-020-1993-0", "professional.txt", "Professional Identity")
    # scrape_to_txt("https://pmc.ncbi.nlm.nih.gov/articles/PMC6373559/", "professional.txt", "Professional Identity")
    # scrape_to_txt("https://www.tandfonline.com/doi/full/10.1080/10872981.2023.2200586", "professional.txt", "Professional Identity")
    # scrape_to_txt("https://builtin.com/articles/how-to-answer-interview-questions", "professional.txt", "Interview Tips")
    # scrape_to_txt("https://ph.jobstreet.com/career-advice/article/how-to-answer-hard-interview-questions-tips-and-samples", "professional.txt", "Interview Tips")
    # scrape_to_txt("https://www.foundit.com.ph/career-advice/common-interview-questions-and-answers/", "professional.txt", "Interview Tips")

    # # --- Family Persona ---
    # scrape_to_txt("https://www.verywellmind.com/can-an-optimist-pessimist-relationship-work-8676482", "family.txt", "Family Support")
    # scrape_to_txt("https://www.verywellmind.com/how-to-be-optimistic-4164832", "family.txt", "Optimism")
    # scrape_to_txt("https://www.verywellmind.com/learned-optimism-4174101", "family.txt", "Learned Optimism")
    # scrape_to_txt("https://www.ncbi.nlm.nih.gov/books/NBK560487/", "family.txt", "Family Health")
    # scrape_to_txt("https://www.healthline.com/health/toxic-family", "family.txt", "Toxic Family")
    # scrape_to_txt("https://www.fosterva.org/blog/how-to-understand-family-systems-and-dynamics", "family.txt", "Family Systems")

    # --- Friend Persona (Optimist) ---
    scrape_to_txt("https://www.lifehack.org/930602/optimist-vs-pessimist", "friend.txt", "Optimist Friend")
    scrape_to_txt("https://www.psychologytoday.com/us/blog/in-the-face-adversity/202108/3-factors-separate-optimists-and-pessimists", "friend.txt", "Optimist Friend")
    scrape_to_txt("https://www.dictionary.com/articles/optimistic-vs-pessimistic/", "friend.txt", "Optimist Friend")

    # --- Friend Persona (Pessimist) ---
    scrape_to_txt("https://www.forbes.com/sites/chriswestfall/2019/07/06/motivate-any-personality-difference-between-optimists-and-pessimists/", "friend.txt", "Pessimist Friend")
    scrape_to_txt("https://www.dictionary.com/articles/optimistic-vs-pessimistic/", "friend.txt", "Pessimist Friend")
    scrape_to_txt("https://sites.psu.edu/aspsy/2024/04/08/a-cynical-optimist/", "friend.txt", "Pessimist Friend")
    # ⚠️ Forbes & Dictionary.com may block scraping — keep PSU link, replace Forbes with PsychologyToday or Medium if needed.

    # # --- Friend Persona (Brainrot) ---
    # scrape_to_txt("https://gamequitters.com/brainrot-slang/", "friend.txt", "Brainrot Friend")
    # scrape_to_txt("https://affine.pro/blog/brain-rot-words-tips", "friend.txt", "Brainrot Friend")

    # # --- You Persona (Past Self) ---
    # scrape_to_txt("https://medium.com/@kat.maren/are-you-kind-to-your-past-self-51b3cf4cdfec", "you.txt", "Past Self")
    # scrape_to_txt("https://www.psychologytoday.com/us/blog/the-power-of-prime/202407/8-steps-to-making-peace-with-your-past-self", "you.txt", "Past Self")
    # scrape_to_txt("https://medium.com/@vishakhasoni284/how-my-past-self-became-motivation-for-my-present-self-74dca409658a", "you.txt", "Past Self")
    # scrape_to_txt("https://www.theblackgirldoctor.com/post/4-reminders-from-my-past-self-that-i-needed-today", "you.txt", "Past Self")
    # scrape_to_txt("https://voiceskopje.org/2025/09/16/a-promise-to-my-past-self/", "you.txt", "Past Self")

    # # --- You Persona (Future Self) ---
    # scrape_to_txt("https://www.mattnorman.com/why-your-future-self-should-be-one-of-your-most-important-relationships/", "you.txt", "Future Self")
    # scrape_to_txt("https://psyche.co/guides/how-to-connect-with-your-future-self-and-make-better-choices", "you.txt", "Future Self")
    # scrape_to_txt("https://medium.com/the-ascent/how-imagining-your-future-self-can-turn-you-into-a-productivity-machine-e19c54de0790", "you.txt", "Future Self")
    # scrape_to_txt("https://elizabethspanncraig.com/motivation-and-the-writing-life/be-kind-to-your-future-self/", "you.txt", "Future Self")

    # # --- Random Persona ---
    # scrape_to_txt("https://arxiv.org/pdf/2502.13270?", "random.txt", "AI Research")
    # scrape_to_txt("https://files.asprtracie.hhs.gov/documents/guide-compassional-empathic-dialog-flash-card-508.pdf", "random.txt", "Empathy Guide")
    # scrape_to_txt("https://medium.com/mind-cafe/how-to-spark-interesting-conversations-with-strangers-b588f8e04994", "random.txt", "Conversation Tips")
    # scrape_to_txt("https://theelizabethday.substack.com/p/132-non-boring-questions-to-start", "random.txt", "Conversation Starters")
    # scrape_to_txt("https://conversationstartersworld.com/250-conversation-starters/", "random.txt", "Conversation Starters")
