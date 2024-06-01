package com.mrguven.mobilelanmonitor.api

import com.mrguven.mobilelanmonitor.model.Client
import com.mrguven.mobilelanmonitor.model.Threat
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface ApiService {
    @GET("/clients")
    suspend fun getClients(): List<Client>

    @GET("/threats")
    suspend fun getThreats(): List<Threat>

    @POST("/client/{ip}/command")
    suspend fun sendCommand(
        @Path("ip") ip: String,
        @Body command: Map<String, String>
    ): Response<Unit>

    companion object {
        private const val BASE_URL = "http://192.168.1.37:5000/"

        fun create(): ApiService {
            val retrofit = Retrofit.Builder()
                .addConverterFactory(GsonConverterFactory.create())
                .baseUrl(BASE_URL)
                .build()

            return retrofit.create(ApiService::class.java)
        }
    }
}
