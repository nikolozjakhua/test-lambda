import toml
import yaml
import sys
import jinja2
import os

def load_toml(file_path):
    """
    Loads a TOML file and returns the parsed content as a dictionary.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"TOML file '{file_path}' not found.")
    
    with open(file_path, 'r') as toml_file:
        return toml.load(toml_file)


def load_yaml(file_path):
    """
    Loads a YAML file and returns the parsed content as a dictionary.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"YAML file '{file_path}' not found.")
    
    with open(file_path, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)


def write_yaml(data, file_path):
    """
    Writes a dictionary to a YAML file.
    """
    with open(file_path, 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)
    print(f"Updated file: {file_path}")


def render_tfvars(template_path, output_path, variables):
    """
    Renders a Jinja2 template using the provided variables.
    
    Args:
        template_path (str): Path to the Jinja2 template file.
        output_path (str): Path to the output file.
        variables (dict): Dictionary of variables to fill in the template.
    """
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file '{template_path}' not found.")
    
    # Load and render the Jinja2 template
    with open(template_path, 'r') as template_file:
        template_content = template_file.read()
    
    template = jinja2.Template(template_content)
    rendered_content = template.render(variables)
    
    # Write the rendered content to the output file
    with open(output_path, 'w') as output_file:
        output_file.write(rendered_content)
    print(f"Generated file: {output_path}")


if __name__ == "__main__":
    # Input and output file paths
    if len(sys.argv) < 4:
        print("Usage: python main.py <isid> <spec_file> <toml_file>")
        sys.exit(1)

    spec_file = sys.argv[2]
    toml_file = sys.argv[3]
    template_file = "terraform.tfvars.j2"
    output_tfvars = f"terraform.{sys.argv[1]}.tfvars"

    backend_file = "terraform.conf.j2"
    output_backend = f"terraform.{sys.argv[1]}.conf"


    # Load data from TOML and YAML files
    toml_data = load_toml(toml_file)
    yaml_data = load_yaml(spec_file)

    # Extract the version from the TOML file
    project_data = toml_data.get("project", {})
    version = project_data.get("version")
    if not version:
        print("No 'version' found in the TOML file.")
        sys.exit(1)

    # Update the YAML file with the version
    yaml_data["version"] = version
    yaml_data["backend"]["key"] = sys.argv[1]
    write_yaml(yaml_data, spec_file)

    
    # Load variables from YAML
    variables = load_yaml(spec_file)
    
    # Render the Jinja2 template for tfvars
    render_tfvars(template_file, output_tfvars, variables)

    # Render the Jinja2 template for backend configuration
    render_tfvars(backend_file, output_backend, variables)