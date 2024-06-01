package com.mrguven.mobilelanmonitor.viewmodel

import android.app.Application
import android.os.Handler
import android.os.Looper
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.mrguven.mobilelanmonitor.model.Client
import com.mrguven.mobilelanmonitor.model.Threat
import com.mrguven.mobilelanmonitor.repository.Repository
import kotlinx.coroutines.launch

class MainViewModel(application: Application, private val repository: Repository) : AndroidViewModel(application) {

    private val _clients = MutableLiveData<List<Client>>()
    val clients: LiveData<List<Client>> get() = _clients

    private val _threats = MutableLiveData<List<Threat>>()
    val threats: LiveData<List<Threat>> get() = _threats

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> get() = _error

    private val handler = Handler(Looper.getMainLooper())
    private val updateInterval: Long = 2000 // 2 saniye

    private val updateRunnable = object : Runnable {
        override fun run() {
            fetchClients()
            fetchThreats()
            handler.postDelayed(this, updateInterval)
        }
    }

    init {
        startUpdatingData()
    }

    private fun startUpdatingData() {
        handler.post(updateRunnable)
    }

    private fun stopUpdatingData() {
        handler.removeCallbacks(updateRunnable)
    }

    fun retryFetchingData() {
        fetchClients()
        fetchThreats()
    }

    private fun fetchClients() {
        viewModelScope.launch {
            try {
                val clients = repository.getClients()
                _clients.postValue(clients)
            } catch (e: Exception) {
                _error.postValue("Failed to fetch clients: ${e.message}")
            }
        }
    }

    private fun fetchThreats() {
        viewModelScope.launch {
            try {
                val threats = repository.getThreats()
                _threats.postValue(threats)
            } catch (e: Exception) {
                _error.postValue("Failed to fetch threats: ${e.message}")
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        stopUpdatingData()
    }
}
