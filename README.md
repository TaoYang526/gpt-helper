# gpt-helper

A command-line interface tool for managing OpenAI GPT assistants, threads, and files.
It integrates with the OpenAI API to perform various operations such as assistant creation, listing, updating, and deletion,
as well as thread and file management.

## Features

- Assistant management operations (create, update, list, delete, choose)
- Thread management operations (create, update, list, delete, choose, chat)
- File management operations (create, update, list, delete)

## Getting Started

### Prerequisites

To run this tool, you will need:

- Python 3.x
- OpenAI API Key (set as an environment variable `OPENAI_API_KEY`)

### Installation

1. Clone the repository and then install.

```bash
git clone <repository-url>
cd gpt-helper && pip3 install .
```

### Usage

#### Required Environment Variables
Set up your OpenAI API key as an environment variable.

```bash
export OPENAI_API_KEY='your-api-key-here'
```

#### gptctl
To interact with ChatGPT, run the `gptctl` command with the desired subcommands. Here's how you can use different parts of the tool:


##### File Commands

```bash
gptctl file --create --path <path-to-local-file>
gptctl file --list
gptctl file --delete --id <file-id>
```

##### Thread Commands

```bash
gptctl thread --create --name <thread-name>
gptctl thread --list
gptctl thread --chat --id <thread-id>
```

##### Assistant Commands

```bash
gptctl assistant --create --name <assistant-name>
gptctl assistant --list
gptctl assistant --delete --id <assistant-id>
```

For more information, you can use the `--help` flag to get a description of all the available subcommands and options. 

## Contributing

Contributions are welcome! Feel free to fork the project and submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## Contact

- taoyang@apache.org
