export const API_BASE = "http://127.0.0.1:5000";

// Size and provenance of the curated library in
// backend/data/raw/article_links.json. Update both if the registry changes.
export const SOURCE_COUNT = 150;

export const PUBLISHERS = ["WHO", "NHS", "Harvard", "CDC", "NIDDK"];

// Mirrors backend/ingestion/categories.py — the knowledge base is curated
// against exactly these 18 categories.
export const CATEGORIES = [
  "Healthy Diet",
  "Nutrition",
  "Food & Nutrients",
  "Fitness & Exercise",
  "Mental Health",
  "Sleep Health",
  "Heart Health",
  "Common Diseases",
  "Common Symptoms",
  "Immunity & Prevention",
  "Hydration",
  "Weight Management",
  "Women's Health",
  "Men's Health",
  "Child Health",
  "Senior Health",
  "Digestive Health",
  "Lifestyle & Wellness",
];

// Shown on the empty state. Each maps onto a category the retriever can
// actually answer from, so a first-time user does not hit
// "I do not have enough trusted information".
export const SUGGESTIONS = [
  {
    category: "Hydration",
    question: "How much water should I drink each day?",
  },
  {
    category: "Sleep Health",
    question: "What are good sleep hygiene habits?",
  },
  {
    category: "Fitness & Exercise",
    question: "What are the health benefits of regular exercise?",
  },
  {
    category: "Heart Health",
    question: "Which foods help lower blood pressure?",
  },
];
