import csv
import argparse
from xml.etree import ElementTree


class AppHostParser:
    def __init__(self, config_file, output_file):
        self.config_file = config_file
        self.output_file = output_file
        self.bind_data = []

    def run(self):
        with open(self.config_file, 'rb') as f:
            root = ElementTree.fromstring( f.read() )
        self.parse_site(root)

        with open(self.output_file, 'w', newline='') as f:
            fc = csv.DictWriter(f, self.bind_data[0].keys())
            fc.writeheader()
            fc.writerows(self.bind_data)

    def parse_site(self, root):
        for site in root.iter(tag='site'):
            site_data = {
                "id": site.get('id'),
                "alias": site.get('name'),
            }
            
            # get virtual directory from site
            v_dir = site.find('application').find('virtualDirectory')
            site_data.update( 
                {
                    "path": v_dir.get('physicalPath'),
                    "user": v_dir.get('userName')
                }
            )
            for binding in site.find('bindings'):
                self.parse_binding(binding, site_data)
    
    def parse_binding(self, binding, site_data):
        # write individual binding informations
        info = binding.get('bindingInformation')
        ip, port, domain = info.split(":")
        self.bind_data.append( {
            "id": site_data['id'],
            "alias": site_data['alias'],
            "path": site_data['path'],
            "user": site_data['user'],
            "protocol": binding.get('protocol'),
            "ip": ip,
            "port": port,
            "domain": domain
        } )

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        IIS-ApphostParser is a tool that parse the applicationhost.config and generates a CSV.
        """
    )
    parser.add_argument(
        '-f', '--file', 
        help='applicationhost.config file.', 
        required=True,
        dest="config_file"
    )
    parser.add_argument(
        '-o', '--output_file', 
        help='name of output file.', 
        default=f"output.csv",
        dest="out_path"
    )
    args = parser.parse_args()
    
    apphostparser = AppHostParser(
        config_file=args.config_file,
        output_file=args.out_path
    )
    apphostparser.run()
    print("[+] Done.")