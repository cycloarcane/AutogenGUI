
# AutoGen Derived GUI Scripts and Binaries

```
       d8888          888                                        .d8888b.  888     888 8888888 
      d88888          888                                       d88P  Y88b 888     888   888   
     d88P888          888                                       888    888 888     888   888   
    d88P 888 888  888 888888 .d88b.   .d88b.   .d88b.  88888b.  888        888     888   888   
   d88P  888 888  888 888   d88""88b d88P"88b d8P  Y8b 888 "88b 888  88888 888     888   888   
  d88P   888 888  888 888   888  888 888  888 88888888 888  888 888    888 888     888   888   
 d8888888888 Y88b 888 Y88b. Y88..88P Y88b 888 Y8b.     888  888 Y88b  d88P Y88b. .d88P   888   
d88P     888  "Y88888  "Y888 "Y88P"   "Y88888  "Y8888  888  888  "Y8888P88  "Y88888P"  8888888 
                                          888                                                  
                                     Y8b d88P                                                  
                                      "Y88P"
```

Welcome to the repository containing Microsoft's AutoGen derived GUI scripts and binaries. This repository offers a variety of functionalities.

## Application Safety Guide

- **Green Colour Scheme**: Generally safe to run, as these applications do not have code execution functionality.
- **Red or Scary Colour Scheme**: Be cautious. Applications with 'Exec' in the name and/or a red or scary colour scheme may modify your system or perform malicious and dangerous actions.

## Main Project

For more details and the main AutoGen project, visit: [Microsoft AutoGen](https://github.com/microsoft/autogen/)

---

## How to Use

1. **Download the repository**:
   ```sh
   git clone https://github.com/cycloarcane/AutogenGUI.git
   ```

2. **Navigate to the directory**:
   ```sh
   cd AutogenGUI
   ```

3. **Run safe applications**:
   - Look for applications without Exec in the title.

4. **Be cautious with exec applications**:
   - Ensure you understand the potential risks before running applications with 'Exec' in the name or a red/scary colour scheme.

5. **Create a virtual environment and activate it**:
   ```sh
   python3 -m venv venv
   ```
   ```sh
   source venv/bin/activate
   ```

6. **Install requirements**
   ```sh
   pip install -r requirements
   ```
7. **Run chosen script**
   ```sh
   python3 3AgentGC.py
   ```
8. **You will need an opensource OpenAI compatible backend**
   - For example [OobaBooga](https://github.com/oobabooga/text-generation-webui)
   - Follow the instructions to get a compatible API and make sure you append /v1 in the GUI when you set the base URL

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a new branch** (`git checkout -b feature-branch`)
3. **Make your changes**
4. **Commit your changes** (`git commit -m 'Add some feature'`)
5. **Push to the branch** (`git push origin feature-branch`)
6. **Open a pull request**

## Contact

For more information or any queries, feel free to reach out:


- **Email:** cycloarkane@gmail.com
- **GitHub Issues**: [AutoGen Derived GUI Scripts Issues](https://github.com/cycloarcane/AutogenGUI/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the contributors who make this project possible.
- Special thanks to Microsoft for the AutoGen project.
