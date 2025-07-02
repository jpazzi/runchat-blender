# ui/helpers.py

import re
import textwrap


def _label_multiline(context, text, parent):
    """
    Display multiline text that automatically wraps based on panel width.
    Based on the solution from https://b3d.interplanety.org/en/multiline-text-in-blender-interface-panels/
    """
    chars = int(context.region.width / 7)   # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        parent.label(text=text_line)


def draw_description_line(layout, line, context=None):
    """Draw a description line with markdown link support and proper multiline wrapping"""
    
    # Find all markdown links in the format [text](url)
    # More robust pattern that handles optional whitespace and empty groups
    link_pattern = r'\[([^\]]*)\]\(([^)]*)\)'
    links = list(re.finditer(link_pattern, line))
    
    # Filter out completely empty links
    valid_links = []
    for link in links:
        link_text = link.group(1).strip() if link.group(1) else ""
        link_url = link.group(2).strip() if link.group(2) else ""
        # Only include links that have at least some text or URL
        if link_text or link_url:
            valid_links.append(link)
    
    links = valid_links
    
    if not links:
        # No links, use the improved multiline text display
        if context:
            _label_multiline(context, line, layout)
        else:
            # Fallback to old method if no context available
            if len(line) > 80:
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line + word) > 80 and current_line:
                        layout.label(text=current_line.strip())
                        current_line = word + " "
                    else:
                        current_line += word + " "
                if current_line.strip():
                    layout.label(text=current_line.strip())
            else:
                layout.label(text=line)
    else:
        # Line contains links, need to create a mixed layout
        # For lines with links, we'll process each segment separately
        last_end = 0
        for link_match in links:
            # Handle text before the link
            before_text = line[last_end:link_match.start()]
            if before_text.strip():
                if context:
                    _label_multiline(context, before_text.strip(), layout)
                else:
                    layout.label(text=before_text.strip())
            
            # Add the link as a clickable button
            link_text = link_match.group(1)
            link_url = link_match.group(2)
            
            # Validate the extracted link components
            if not link_text or not link_text.strip():
                link_text = "Link"  # Default text for empty link text
            
            if not link_url or not link_url.strip():
                # No valid URL, just show as regular text
                layout.label(text=f"[{link_text}]")
            else:
                # Clean up the URL (remove any whitespace)
                link_url = link_url.strip()
                
                # Validate URL format (basic check)
                if not (link_url.startswith('http://') or link_url.startswith('https://') or link_url.startswith('www.') or '.' in link_url):
                    # Invalid URL format, show as regular text
                    layout.label(text=f"[{link_text}]({link_url})")
                else:
                    # Create a custom operator for this specific link
                    try:
                        row = layout.row()
                        row.alignment = 'LEFT'
                        link_op = row.operator("runchat.open_link", text=link_text, icon="URL")
                        if link_op:
                            link_op.url = link_url
                        else:
                            # Fallback to regular text if operator fails
                            row.label(text=f"{link_text} ({link_url})")
                    except Exception as e:
                        # Fallback to regular text if operator registration fails
                        layout.label(text=f"{link_text} ({link_url})")
            
            last_end = link_match.end()
        
        # Add any remaining text after the last link
        remaining_text = line[last_end:]
        if remaining_text.strip():
            if context:
                _label_multiline(context, remaining_text.strip(), layout)
            else:
                layout.label(text=remaining_text.strip())


def format_text_output(layout, text_value, max_lines=10, context=None):
    """Format text output with improved multiline support"""
    text_lines = text_value.split('\n')
    
    # Use improved multiline display if context is available
    if context:
        # Create a column with tight spacing for better readability
        col = layout.column(align=True)
        
        for line_num, line in enumerate(text_lines[:max_lines]):
            if line.strip():  # Only process non-empty lines
                _label_multiline(context, line, col)
            else:
                # Show empty line
                col.label(text="")
    else:
        # Fallback to old method
        for line_num, line in enumerate(text_lines[:max_lines]):
            if len(line) > 80:
                # Split long lines
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line + word) > 80 and current_line:
                        layout.label(text=current_line.strip())
                        current_line = word + " "
                    else:
                        current_line += word + " "
                if current_line.strip():
                    layout.label(text=current_line.strip())
            else:
                layout.label(text=line)
    
    if len(text_lines) > max_lines:
        layout.label(text=f"... and {len(text_lines) - max_lines} more lines")


def format_multiline_text(context, text, parent, max_lines=None):
    """
    Enhanced multiline text formatter with word wrapping based on panel width.
    This is the main function to use for displaying any multiline text in Blender panels.
    
    Args:
        context: Blender context (for getting panel width)
        text: The text to display
        parent: The UI layout element to add text to
        max_lines: Optional maximum number of lines to display
    """
    if not text or not text.strip():
        parent.label(text="(No text)")
        return
    
    # Split text into lines first
    lines = text.split('\n')
    
    # Limit lines if specified
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        truncated = True
    else:
        truncated = False
    
    # Create a tightly spaced column for better readability
    col = parent.column(align=True)
    
    # Process each line with proper word wrapping
    for line in lines:
        if line.strip():  # Only process non-empty lines
            _label_multiline(context, line, col)
        else:
            # Preserve empty lines
            col.label(text="")
    
    # Show truncation notice if needed
    if truncated:
        col.label(text=f"... and {len(text.split(chr(10))) - max_lines} more lines")


def create_collapsible_section(layout, prop_name, icon_expanded, icon_collapsed, text, expanded_prop):
    """Create a collapsible section header"""
    header = layout.row()
    header.prop(expanded_prop, prop_name, 
               icon=icon_expanded if getattr(expanded_prop, prop_name) else icon_collapsed, 
               emboss=False)
    header.label(text=text)
    return getattr(expanded_prop, prop_name) 