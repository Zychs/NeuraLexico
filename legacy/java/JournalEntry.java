import java.io.Serializable;
import java.util.Date;

public class JournalEntry implements Serializable {
    private String title;
    private String content;
    private Date date;

    public JournalEntry(String title, String content) {
        this.title = title;
        this.content = content;
        this.date = new Date();
    }

    public String getTitle() {
        return title;
    }

    public String getContent() {
        return content;
    }

    public Date getDate() {
        return date;
    }

    @Override
    public String toString() {
        return "Date: " + date + "\nTitle: " + title + "\nContent: " + content;
    }
}
