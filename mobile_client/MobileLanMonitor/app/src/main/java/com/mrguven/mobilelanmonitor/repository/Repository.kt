package com.mrguven.mobilelanmonitor.repository

import com.mrguven.mobilelanmonitor.api.ApiService
import com.mrguven.mobilelanmonitor.model.Client
import com.mrguven.mobilelanmonitor.model.Threat

class Repository(private val apiService: ApiService) {
    suspend fun getClients(): List<Client> = apiService.getClients()
    suspend fun getThreats(): List<Threat> = apiService.getThreats()
}
