import os
import glob

def sync_rules():
    """
    Syncs markdown references to Cursor .mdc rules.
    This allows Cursor to automatically apply these rules when relevant files are edited.
    """
    ref_dir = "references"
    cursor_dir = ".cursor/rules"
    
    if not os.path.exists(cursor_dir):
        os.makedirs(cursor_dir)
        print(f"Created {cursor_dir}")

    # Process specialized tracks
    for md_file in glob.glob(f"{ref_dir}/*.md"):
        base_name = os.path.basename(md_file)
        rule_name = base_name.replace(".md", ".mdc")
        
        with open(md_file, 'r') as f:
            content = f.read()
            
        # Add cursor-specific metadata if needed, but for now just copy content
        # Official VTEX rules use specific globs. We can infer them.
        globs = ""
        if "faststore" in base_name:
            globs = "discovery.config.js, src/**/*, cms/**/*"
        elif "io-development" in base_name:
            globs = "manifest.json, node/**/*, react/**/*, graphql/**/*"
        elif "store-framework" in base_name:
            globs = "store/blocks/**/*, styles/css/**/*"
            
        header = f"---\ndescription: VTEX {base_name.replace('.md', '').capitalize()} Best Practices\nglobs: {globs}\n---\n\n"
        
        with open(os.path.join(cursor_dir, rule_name), 'w') as f:
            f.write(header + content)
        
        print(f"Synced {rule_name}")

    # Sync main orchestrator
    with open("SKILL.md", 'r') as f:
        content = f.read()
    with open(os.path.join(cursor_dir, "vtex-main.mdc"), 'w') as f:
        f.write("---\ndescription: Global VTEX Development Rules\nglobs: **/*\n---\n\n" + content)
    print("Synced vtex-main.mdc")

if __name__ == "__main__":
    sync_rules()
