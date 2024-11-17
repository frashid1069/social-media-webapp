import { getAuthorId } from "./Stream";

class Author {
    constructor({ author }) {
      this.type = "author";
      this.id = author.id;
      this.displayName = author.displayName;
      this.github = author.github || null;
      this.profileImage = author.profileImage || null;
      this.host = author.host;
      this.page = `${this.host}authors/${this.getAuthorId(this.id)}`; // Generating the page URL
    }

    toJSON() {
        // Return a plain object for API calls
        return {
          type: this.type,
          id: this.id,
          displayName: this.displayName,
          github: this.github,
          profileImage: this.profileImage,
          host: this.host,
          page: this.page,
        };
      }
  }
  