# Facebook Page and Group's Post Scraper

This is a simple script to gather all comments of a Facebook Page or Group.
The script  outputs the posts in Json file format.


## Initial setup

1. Access to https://developers.facebook.com/ and create a new App.
2. Make sure to have the following permissions active: publish_to_groups, pages_read_user_content, pages_manage_engagement, pages_manage_posts, Page Public Content Access Feature.
3. Create a folder named posts
4. Add app_id and app_secret in scrape_post_and_comment.py script.
5. Add page_id, you can find this in the section of the url in page or group searched  (https://www.facebook.com/!!THIS PART!!/).
6. Lauch script and have fun! :) .

## Usage

Once data are scraped, you can find Json files in /posts/ folder.

## Test
You can test every API here: https://developers.facebook.com/tools/explorer/
