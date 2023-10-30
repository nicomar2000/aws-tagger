# AWS Resource Tagging Utility

This AWS Resource Tagging Utility is an open-source Python script that offers a web-based User Interface for the tagging of AWS resources. The utility addresses tag consistency with suggested values based on existing resource information such like tags, id and descriptions as well as its associated resources information.

## Requirements

For this tagging utility to run, you need:
- Python 3.x installed on your system.
- An AWS CLI profile configured with access to the AWS account you wish to manage resources within.

## Getting Started

Follow the steps below to leverage this tool.

1. Start the script with the following command in a terminal or command line window:

```bash
python main.py
```

2. This will start a local web server on port `8080` of your machine. Open a web browser and navigate to:

```html
http://localhost:8080
```

3. On the opened UI, enter the following details:
    - Profile: This should correspond to you AWS CLI profile configured on your AWS account.
    - AWS regions: Select the region where your resources are located.
    - Resources type: Define what kinds of resources you want to evaluate for tagging. You will also see a dropdown to select the maximum number of associated resources to search for hints. If no hints are found in the resource itself, the script will search for hints within the associated resources based on this number. Select how many associated resources the script should search for tags on each resource type, where if you select the number one, the script would only search for hints on one of the available associated resources. 
    - Tag keys: Define the resources tag key and value you want to evaluate. Here you can provide hints for generating possible values for each tag. The script will generate possible values from these hints or from associated resources hints, and will use one of these values if the tag is not present on a resource
  

## Support & Contribution

This tool is open source and we welcome contributions! Feel free to fork, modify and issue pull requests. If you find a bug or want to request a new feature, please create an issue and we'll respond as promptly as we can.