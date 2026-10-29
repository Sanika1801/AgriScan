import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriscan.settings')
django.setup()

from community.models import ForumPost, ForumComment
from accounts.models import User

def seed_forum():
    # Ensure users exist
    farmer, _ = User.objects.get_or_create(username='farmer_raj', defaults={'role': 'farmer'})
    farmer_dev, _ = User.objects.get_or_create(username='farmer_dev', defaults={'role': 'farmer'})
    expert, _ = User.objects.get_or_create(username='dr_smith', defaults={'role': 'agronomist'})

    posts_data = [
        {
            "title": "White spots on my tomato leaves - is this Late Blight?",
            "content": "I noticed white powdery spots on the lower leaves of my tomato plants yesterday. It has been very humid here. I used the AI scanner and it said 'Tomato Late Blight' with 85% confidence. Does anyone know the best organic treatment for this?",
            "comments": [
                (expert, "Yes, that is Late Blight. You need to act fast. Remove the infected leaves immediately and spray a copper-based fungicide. Avoid watering the leaves directly."),
                (farmer_dev, "I had the same issue last week. I used Neem oil and it helped slow it down."),
            ]
        },
        {
            "title": "Yellowing of wheat crop in Sector 4",
            "content": "My wheat crop is turning yellow from the tips of the leaves. The soil pH is around 6.5. Could this be a nitrogen deficiency or a disease?",
            "comments": [
                (expert, "Yellowing from the tips usually indicates a Nitrogen deficiency. Try applying a urea top-dressing. If it doesn't improve in 3 days, it might be a fungal issue."),
            ]
        },
        {
            "title": "Best organic fertilizer for vegetables?",
            "content": "I want to switch completely to organic farming for my tomatoes and potatoes. What is the best alternative to NPK fertilizers?",
            "comments": [
                (farmer_dev, "Try Vermicompost! It completely transformed my soil quality."),
                (expert, "Vermicompost is excellent. You can also use bone meal for phosphorus and wood ash for potassium."),
            ]
        },
        {
            "title": "How to protect crops from heavy rain?",
            "content": "The weather forecast says heavy rain is coming this weekend. I have just sown new seeds. Any advice on protecting them from washing away?",
            "comments": [
                (farmer_dev, "Create small drainage channels around your field so the water doesn't pool."),
            ]
        },
        {
            "title": "Is the AI scanner working for Apple crops?",
            "content": "I tried the AgriScan AI scanner on my apple tree leaves, and it correctly identified Apple Scab! Just wanted to say this tool is amazing.",
            "comments": [
                (expert, "Glad to hear it! If the AI ever gives low confidence, just book a consultation with me or the other experts."),
            ]
        }
    ]

    print("🌱 Seeding Community Forum...")

    for p_data in posts_data:
        post, created = ForumPost.objects.get_or_create(
            title=p_data["title"],
            defaults={'author': farmer, 'content': p_data["content"]}
        )
        
        if created:
            print(f"✅ Created Post: {post.title}")
            for comment_author, comment_text in p_data["comments"]:
                ForumComment.objects.create(post=post, author=comment_author, content=comment_text)
            print(f"   └─ Added {len(p_data['comments'])} comments")

    print("🎉 Community Forum populated successfully!")

if __name__ == '__main__':
    seed_forum()