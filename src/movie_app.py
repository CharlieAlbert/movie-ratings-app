import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from PIL import Image, ImageTk
import requests
from io import BytesIO


class MovieRatingsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Movie Ratings App")
        self.root.geometry("800x600")

        # Set up data file path - points to data/movies.json
        self.data_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "movies.json"
        )

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

        self.movies = self.load_movies()

        self.setup_ui()
        self.refresh_movie_list()
        self.update_statistics()

    def load_movies(self):
        """Load movies from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading movies: {e}")
                return []
        return []

    def save_movies(self):
        """Save movies to JSON file"""
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.movies, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save movies: {e}")

    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Add Movie", padding="10")
        input_frame.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        ttk.Label(input_frame, text="Movie Title:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(input_frame, textvariable=self.title_var, width=30)
        title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)
        title_entry.bind("<Return>", lambda e: self.add_movie())

        ttk.Label(input_frame, text="Rating (1-5):").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.rating_var = tk.StringVar()
        rating_combo = ttk.Combobox(
            input_frame,
            textvariable=self.rating_var,
            values=["1", "2", "3", "4", "5"],
            width=10,
            state="readonly",
        )
        rating_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=2)

        ttk.Label(input_frame, text="Image URL (optional):").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        self.image_var = tk.StringVar()
        image_entry = ttk.Entry(input_frame, textvariable=self.image_var, width=30)
        image_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=2)

        ttk.Button(input_frame, text="Add Movie", command=self.add_movie).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        # Statistics section
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        self.stats_label = ttk.Label(stats_frame, text="No movies added yet")
        self.stats_label.grid(row=0, column=0, sticky=tk.W)

        button_frame = ttk.Frame(stats_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(
            button_frame, text="Show Top Rated", command=self.show_top_rated
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All", command=self.clear_all_movies).grid(
            row=0, column=1, sticky=tk.W
        )

        # Movies display section
        movies_frame = ttk.LabelFrame(main_frame, text="Your Movies", padding="10")
        movies_frame.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        # Create scrollable frame for movies
        canvas = tk.Canvas(movies_frame, height=300)
        scrollbar = ttk.Scrollbar(movies_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        movies_frame.columnconfigure(0, weight=1)
        movies_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)

        # Focus on title entry for immediate use
        title_entry.focus()

    def add_movie(self):
        """Add a new movie to the list"""
        title = self.title_var.get().strip()
        rating = self.rating_var.get()
        image_url = self.image_var.get().strip()

        if not title or not rating:
            messagebox.showerror("Error", "Please enter both title and rating!")
            return

        # Check if movie already exists
        for movie in self.movies:
            if movie["title"].lower() == title.lower():
                messagebox.showerror("Error", "Movie already exists!")
                return

        movie = {
            "title": title,
            "rating": int(rating),
            "image_url": image_url if image_url else None,
        }

        self.movies.append(movie)
        self.save_movies()
        self.refresh_movie_list()
        self.update_statistics()

        # Clear input fields
        self.title_var.set("")
        self.rating_var.set("")
        self.image_var.set("")

        messagebox.showinfo("Success", f"Added '{title}' with {rating} stars!")

    def refresh_movie_list(self):
        """Refresh the display of movies"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.movies:
            ttk.Label(
                self.scrollable_frame,
                text="No movies added yet. Add some movies to see them here!",
                font=("Arial", 12),
            ).grid(row=0, column=0, pady=20)
            return

        # Sort movies by rating (highest first), then by title
        sorted_movies = sorted(
            self.movies, key=lambda x: (-x["rating"], x["title"].lower())
        )

        for i, movie in enumerate(sorted_movies):
            movie_frame = ttk.Frame(
                self.scrollable_frame, relief="solid", borderwidth=1
            )
            movie_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
            movie_frame.columnconfigure(1, weight=1)

            # Movie image (placeholder if no URL)
            image_label = ttk.Label(movie_frame, text="🎬", font=("Arial", 24))
            if movie.get("image_url"):
                try:
                    response = requests.get(movie["image_url"], timeout=5)
                    img = Image.open(BytesIO(response.content))
                    img = img.resize((80, 120), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    image_label.configure(image=photo, text="")
                    image_label.image = photo  # Keep a reference
                except Exception as e:
                    print(f"Could not load image for {movie['title']}: {e}")

            image_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

            # Movie title
            title_label = ttk.Label(
                movie_frame, text=movie["title"], font=("Arial", 14, "bold")
            )
            title_label.grid(
                row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=(10, 5)
            )

            # Movie rating
            stars = "⭐" * movie["rating"] + "☆" * (5 - movie["rating"])
            rating_label = ttk.Label(
                movie_frame, text=f"{stars} ({movie['rating']}/5)", font=("Arial", 12)
            )
            rating_label.grid(
                row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=(0, 10)
            )

            # Delete button
            ttk.Button(
                movie_frame, text="Delete", command=lambda m=movie: self.delete_movie(m)
            ).grid(row=0, column=2, rowspan=2, padx=10, pady=10)

    def delete_movie(self, movie):
        """Delete a movie from the list"""
        if messagebox.askyesno("Confirm Delete", f"Delete '{movie['title']}'?"):
            self.movies.remove(movie)
            self.save_movies()
            self.refresh_movie_list()
            self.update_statistics()

    def clear_all_movies(self):
        """Clear all movies from the list"""
        if self.movies and messagebox.askyesno(
            "Confirm Clear All", "Delete ALL movies? This cannot be undone!"
        ):
            self.movies.clear()
            self.save_movies()
            self.refresh_movie_list()
            self.update_statistics()

    def update_statistics(self):
        """Update statistics display"""
        if not self.movies:
            self.stats_label.configure(text="No movies added yet")
            return

        total_movies = len(self.movies)
        average_rating = sum(movie["rating"] for movie in self.movies) / total_movies
        top_rated = max(self.movies, key=lambda x: x["rating"])

        # Count by rating
        rating_counts = {i: 0 for i in range(1, 6)}
        for movie in self.movies:
            rating_counts[movie["rating"]] += 1

        stats_text = (
            f"Total Movies: {total_movies} | Average Rating: {average_rating:.1f}/5 | "
            f"Top Rated: '{top_rated['title']}' ({top_rated['rating']}/5)"
        )
        self.stats_label.configure(text=stats_text)

    def show_top_rated(self):
        """Show top rated movies in a popup"""
        if not self.movies:
            messagebox.showinfo("Top Rated", "No movies to show!")
            return

        # Get movies with highest rating
        max_rating = max(movie["rating"] for movie in self.movies)
        top_movies = [movie for movie in self.movies if movie["rating"] == max_rating]

        if len(top_movies) == 1:
            message = f"Top rated movie:\n'{top_movies[0]['title']}' - {max_rating}/5 stars ⭐"
        else:
            titles = [movie["title"] for movie in top_movies]
            message = f"Top rated movies ({max_rating}/5 stars ⭐):\n\n" + "\n".join(
                f"• {title}" for title in titles
            )

        # Show genre analysis if enough movies
        if len(self.movies) >= 3:
            genre_hint = "\n\nTip: Add more movies to discover your favorite genres!"
            message += genre_hint

        messagebox.showinfo("Top Rated Movies", message)


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = MovieRatingsApp(root)

    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
