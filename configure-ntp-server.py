
from support import logger, from_json, validate_json_schema;
import os;
import sys;
import jinja2;

class configure_ntp_servers:
    def __init__(self):
        self.ntp_servers = from_json("config/ntp-servers.json")["ntp-servers"];
        self.download_and_install_ntp_server();

    def download_and_install_ntp_server(self):
        logger.info("Update the system repositories and install the NTP software.");
        os.system("sudo apt update");
        os.system("sudo apt install ntp -y");
        self.prepare_and_replace_ntp_configuration();

    def prepare_and_replace_ntp_configuration(self):
        logger.info("Prepare and replace the NTP configuration file \"/etc/ntp.conf\".");
        self.render_and_replace_system_files("template/ntp.conf", "/etc/ntp.conf", ntp_servers=self.ntp_servers);
        self.restart_ntp_service();

    def render_and_replace_system_files(self, template, path, **kargs):
        if os.path.exists(template):
            with open(template, "r") as file:
                template = jinja2.Template(file.read());
            os.system(f"cp {path} {path}_$(date +'%Y%m%d')");
            with open(path, "w") as file:
                file.write(template.render(**kargs));
        else:
            logger.critical("The template doesn't exist for the NTP configuration file \"{path}\".");
            sys.exit(1);

    def restart_ntp_service(self):
        logger.info("Restart the NTP service and validate.");
        os.system("sudo systemctl restart ntp");

def main():
    validate_json_schema("config/ntp-servers.json", "schema/ntp-servers-schema.json");
    configure_ntp_servers();

if "__main__" in __name__:
    if os.geteuid() != 0:
        logger.critical("Please execute a script with root privileges.");
    else:
        main();