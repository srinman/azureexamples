data "azurerm_cosmosdb_account" "cosmosdb1" {
  name                = "srinmancosmosmongo"
  resource_group_name = "blkrg"
}

data "azurerm_log_analytics_workspace" "log1" {
  name                = "acalogs"
  resource_group_name = "acarg"
}

resource "azurerm_monitor_diagnostic_setting" "diag1" {
  name                       = "diagtf1"
  target_resource_id         = data.azurerm_cosmosdb_account.cosmosdb1.id
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.log1.id

  log {
    category = "DataPlaneRequests"
    enabled  = true
  }

  log {
    category = "ControlPlaneRequests"
    enabled  = true
  }

    log {
    category = "MongoRequests"
    enabled  = true

  }
}