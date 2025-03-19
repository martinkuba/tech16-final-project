import {
	App,
	Plugin,
	WorkspaceLeaf,
	ItemView,
  MarkdownView,
} from "obsidian";

const VIEW_TYPE_CHAT = "llm-chat-view";

class ChatView extends ItemView {
	private chatListEl: HTMLElement;
	private inputEl: HTMLTextAreaElement;
	private sendButtonEl: HTMLButtonElement;
	private clearButtonEl: HTMLButtonElement;
  private typeEl: HTMLSelectElement;

	getViewType(): string {
		return VIEW_TYPE_CHAT;
	}

	getDisplayText(): string {
		return "LLM Chat";
	}

  async onOpen() {
    // Use the view container to create the UI elements
    const container = this.containerEl.children[1];
    container.empty();
    container.addClass("chat-container");

    container.createEl("h3", { text: "LLM Chat" });

    // Create a container for the chat messages
    this.chatListEl = container.createEl("div", { cls: "chat-list" });

    // Create a container for the input field and send button
    const bottomContainer = container.createEl("div", { cls: "bottom-container" });

    this.inputEl = bottomContainer.createEl("textarea", {
        placeholder: "Type your message..."
    });

    const inputContainer = bottomContainer.createEl("div", { cls: "chat-input-container" });
    
    this.typeEl = inputContainer.createEl("select", { cls: "chat-input-type" });
    this.typeEl.createEl("option", { text: "Discuss current note", value: "current-note" });
    this.typeEl.createEl("option", { text: "Discuss all notes", value: "all-notes" });
    this.typeEl.createEl("option", { text: "Search for notes", value: "find-files" });

    this.inputEl.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
          event.preventDefault(); // Prevents line break in input
          this.onSend();
      }
    });

    this.sendButtonEl = inputContainer.createEl("button", { text: "Send" });
    this.sendButtonEl.onclick = () => this.onSend();

    this.clearButtonEl = inputContainer.createEl("button", { text: "Clear" });
    this.clearButtonEl.onclick = () => this.onClear();

    container.appendChild(bottomContainer);
  }

  async onSend() {
    const prompt = this.inputEl.value.trim();
    if (!prompt) return;

    let context;
    const type = this.typeEl.value;
    if (type == 'current-note') {
      context = await this.getActiveNoteText();
    }

    // Create user message and append to chat
    const userMessageEl = createEl("div", { cls: "chat-message user", text: `${prompt}` });
    userMessageEl.style.whiteSpace = "pre-wrap"; // Preserve line breaks and whitespace
    this.chatListEl.appendChild(userMessageEl);
    this.inputEl.value = "";

    // Auto-scroll to the latest message
    this.chatListEl.scrollTop = this.chatListEl.scrollHeight;

    // Send the prompt to the HTTP endpoint
    try {
        const response = await fetch("http://localhost:8181/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt, type, context })
        });

        if (response.ok) {
            const data = await response.json();
            // console.log('data', data)

            if (type == 'find-files') {
              const listEl = createEl("ul");
              this.chatListEl.appendChild(listEl);
              data.response.forEach((name: string) => {
                  const listItem = listEl.createEl("li");
                  const link = listItem.createEl("a", { text: name, href: "#" });

                  link.addEventListener("click", (event) => {
                      event.preventDefault();
                      this.app.workspace.openLinkText(name, "", false);
                  });
              });
            } else {
              // Append the response message to the chat list
              const responseEl = createEl("div", { cls: "chat-message response", text: `${data.response}` });
              responseEl.style.whiteSpace = "pre-wrap"; // Preserve line breaks and whitespace
              this.chatListEl.appendChild(responseEl);
              
              // If sources are available (for RAG responses), display them
              if (data.sources && data.sources.length > 0) {
                const sourcesContainer = createEl("div", { cls: "sources-container" });
                const sourcesTitle = createEl("div", { cls: "sources-title", text: "Sources:" });
                sourcesContainer.appendChild(sourcesTitle);
                
                const sourcesList = createEl("ul", { cls: "sources-list" });
                data.sources.forEach((source: string) => {
                  const sourceItem = sourcesList.createEl("li");
                  const sourceLink = sourceItem.createEl("a", { text: source, href: "#" });
                  
                  sourceLink.addEventListener("click", (event) => {
                    event.preventDefault();
                    this.app.workspace.openLinkText(source, "", false);
                  });
                });
                
                sourcesContainer.appendChild(sourcesList);
                this.chatListEl.appendChild(sourcesContainer);
              }
            }
        } else {
            const errorEl = createEl("div", { cls: "chat-message error", text: "Error: " + response.statusText });
            this.chatListEl.appendChild(errorEl);
        }
    } catch (error) {
        const errorEl = createEl("div", { cls: "chat-message error", text: "Network error" });
        this.chatListEl.appendChild(errorEl);
    }

    // Auto-scroll to the latest message
    this.chatListEl.scrollTop = this.chatListEl.scrollHeight;
  }

  async onClear() {
    this.chatListEl.innerHTML = "";
  }

  async getActiveNoteText() {
    // const file = this.app.workspace.lastActiveFile;
    // console.log('file:', file);

    const activeFile = this.app.workspace.getActiveFile();
    // console.log('activeFile: ', activeFile);

    if (!activeFile) {
        console.log("No active note open.");
        return null;
    }

    // Read the content of the file
    const content = await this.app.vault.read(activeFile);
    // console.log("Note content:", content);
    return content;
  }
}

export default class ChatPlugin extends Plugin {
	async onload() {
		// Register the custom view
		this.registerView(VIEW_TYPE_CHAT, (leaf: WorkspaceLeaf) => new ChatView(leaf));

		// (Optional) Add a ribbon icon to quickly open the chat view
		this.addRibbonIcon("message-square", "LLM Chat", () => {
			this.activateView();
		});
	}

	async onunload() {
		this.app.workspace.detachLeavesOfType(VIEW_TYPE_CHAT);
	}

	async activateView() {
		let leaf = this.app.workspace.getLeavesOfType(VIEW_TYPE_CHAT)[0];
		if (!leaf) {
			// Open a new right sidebar leaf with the chat view if it doesn't exist
			await this.app.workspace.getRightLeaf(false).setViewState({
				type: VIEW_TYPE_CHAT,
				active: true,
			});
			leaf = this.app.workspace.getLeavesOfType(VIEW_TYPE_CHAT)[0];
		}
		this.app.workspace.revealLeaf(leaf);
	}
}
