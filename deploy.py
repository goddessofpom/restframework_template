import os
import json


class DeployTool(object):
  def __init__(self):
    with open("config.json", "r") as f:
      self.config = json.load(f)

  def deploy(self):
    project_name = self.config.get("project_name")
    image_tag = self.config.get("image_tag")
    docker_hub_url = self.config.get("docker_hub_url")

    os.system('docker-compose build')
    print("finish build image")

    os.system('docker tag %s:%s %s/%s:%s' % (project_name, image_tag, docker_hub_url, project_name, image_tag))
    os.system('docker push %s/%s:%s' % (docker_hub_url, project_name, image_tag))
    print("finish upload image")

    update_services = self.config.get("update_services", [])
    services_name = ' '.join(update_services)
    update_command = 'docker stack deploy docker-stack.yml %s' % (services_name, )
    print("update services finish")

if __name__ == '__main__':
  tool = DeployTool()
  tool.deploy()
