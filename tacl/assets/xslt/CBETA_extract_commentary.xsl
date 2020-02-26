<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output encoding="UTF-8" method="xml" />

  <!-- Keep only text that occurs within tei:note[@place='inline'],
       unless the inverse parameter is true, in which case, keep only
       text that does not occur in tei:note[@place='inline']. Keep as
       much structure as possible without having masses of empty
       elements. -->

  <xsl:param name="inverse" select="0" />

  <xsl:template match="tei:text">
    <xsl:copy>
      <xsl:apply-templates select="@*" />
      <xsl:choose>
        <xsl:when test="$inverse">
          <xsl:apply-templates mode="inverse" select="node()" />
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates mode="commentary" select="node()" />
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="tei:note[@place='inline']" mode="commentary">
    <xsl:variable name="current-note-id" select="generate-id(.)" />
    <xsl:copy-of select="preceding::tei:lb[1][generate-id(following::tei:note[@place='inline'][1]) = $current-note-id]" />
    <xsl:copy-of select="." />
  </xsl:template>

  <xsl:template match="*" mode="commentary">
    <xsl:if test=".//tei:note[@place='inline']">
      <xsl:copy>
        <xsl:apply-templates mode="commentary" select="@*|node()" />
      </xsl:copy>
    </xsl:if>
  </xsl:template>

  <xsl:template match="@*" mode="commentary">
    <xsl:copy />
  </xsl:template>

  <xsl:template match="text()" mode="commentary" />

  <xsl:template match="tei:note[@place='inline']" mode="inverse">
    <xsl:copy-of select=".//tei:lb[position()=last()]" />
  </xsl:template>

  <xsl:template match="@*|node()" mode="inverse">
    <xsl:copy>
      <xsl:apply-templates mode="inverse" select="@*|node()" />
    </xsl:copy>
  </xsl:template>

  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
