## Block

A block object represents a piece of content within Notion. The API translates the headings, toggles, paragraphs, lists, media, and more that you can interact with in the Notion UI as different [block type objects](https://developers.notion.com/reference/block#block-type-objects).

For example, the following block object represents a Heading 2 in the Notion UI:

Use the [Retrieve block children](https://developers.notion.com/reference/get-block-children) endpoint to list all of the blocks on a page.

### Block types that support child blocks
Some block types contain nested blocks. The following block types support child blocks:

- Bulleted list item 
- Callout 
- Child database 
- Child page 
- Column 
- Heading 1, when the is_toggleable property is true 
- Heading 2, when the is_toggleable property is true 
- Heading 3, when the is_toggleable property is true 
- Numbered list item 
- Paragraph 
- Quote 
- Synced block 
- Table 
- Template 
- To do 
- Toggle

## Rich text

Notion uses rich text to allow users to customize their content.  Rich text refers to a type of document where content can be styled and formatted in a variety of customizable ways.  
This includes styling decisions, such as the use of italics, font size, and font color, as well as formatting, such as the use of hyperlinks or code blocks.

Notion includes rich text objects in block objects to indicate how blocks in a page are represented.  
Blocks that support rich text will include a rich text object; **however, not all block types offer rich text**.

支持rich_text的block:  

- Bulleted list item
- Callout 
- Headings
- Numbered list item  
- Paragraph  
- Quote  
- To do  
- Toggle blocks

When blocks are retrieved from a page using the Retrieve a block or [Retrieve block children](https://developers.notion.com/reference/get-block-children) endpoints, an array of rich text objects will be included in the block object (when available).  
Developers can use this array to retrieve the plain text (plain_text) for the block or get all the rich text styling and formatting options applied to the block.

```json5
{
  "type": "text",
  "text": {
    "content": "Some words ",
    "link": null
  },
  "annotations": {
    "bold": false,
    "italic": false,
    "strikethrough": false,
    "underline": false,
    "code": false,
    "color": "default"
  },
  "plain_text": "Some words ",
  "href": null
}
```