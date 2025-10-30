// Add this to your existing template instead of App Service Plan + App Service
@description('Creates an Azure Container Instance for the application.')
resource containerInstance 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: '${uniqueString(resourceGroup().id)}-aci'
  location: location
  properties: {
    containers: [
      {
        name: 'zava-app'
        properties: {
          image: 'nginx:latest' // Placeholder - replace with your actual image when ready
          ports: [
            {
              protocol: 'TCP'
              port: 80
            }
          ]
          environmentVariables: [
            {
              name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
              value: appInsights.properties.InstrumentationKey
            }
          ]
          resources: {
            requests: {
              memoryInGB: 1
              cpu: 1
            }
          }
        }
      }
    ]
    osType: 'Linux'
    restartPolicy: 'Always'
    ipAddress: {
      ports: [
        {
          protocol: 'TCP'
          port: 80
        }
      ]
      type: 'Public'
    }
  }
}

output containerInstanceFqdn string = containerInstance.properties.ipAddress.fqdn
